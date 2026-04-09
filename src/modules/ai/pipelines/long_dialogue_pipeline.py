"""
Многошаговый пайплайн для длинных транскриптов при GigaChat RAG.

Проблема: create_retrieval_chain эмбеддит весь `input` → лимит ~514 токенов на embeddings.
Решение: короткий фиксированный запрос к retriever; длинный текст режется на блоки;
каждый блок идёт в chat без эмбеддинга всего текста; затем агрегация и финал.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from src.modules.ai.model.prompts import RECOMMENDATION_SYSTEM_PROMPT, RESUME_SYSTEM_PROMPT
from src.modules.ai.utils.langchain_helpers import extract_result


# Запрос к Chroma только короткий — укладывается в лимит GigaChat embeddings
SHORT_RAG_QUERY = (
    "резюме звонка продажи ГАРАНТ презентация продукт договорённости возражения клиент"
)

# Если транскрипт длиннее — включаем пайплайн (запас до лимита эмбеддинга на «вопрос»)
TRANSCRIPT_CHAR_THRESHOLD = 900

# Размер фрагмента для поэтапного анализа (в символах; в chat, не в embeddings)
SEGMENT_MAX_CHARS = 2800
SEGMENT_OVERLAP = 250


BLOCK_RESUME_INSTRUCTIONS = """Дай КРАТКИЙ маркированный список только фактов из этого фрагмента:
- этап разговора / роль собеседника (если понятно)
- что предложил менеджер (продукты, демо, КП)
- возражения и реакция клиента
- любые договорённости, даты, «перезвонить»
Не дублируй дословно весь фрагмент. Только выжимка."""


AGGREGATE_RESUME_PREFIX = """У тебя несколько блоков заметок по одному звонку (транскрипт разбит по частям).
Объедини их в одну согласованную сводку:
- убери повторы
- выстрой логичный порядок
- отметь противоречия, если есть

Блоки заметок:
---
"""

AGGREGATE_RESUME_SUFFIX = """

---
Результат — связный текст заметок (не итоговое резюме для клиента), до 2000 слов."""


BLOCK_RECOMMENDATION_INSTRUCTIONS = """Кратко (маркированный список):
- этап: секретарь / ЛПР / неясно
- ошибки или слабые места менеджера в ЭТОМ фрагменте
- 1–2 конкретные рекомендации по улучшению для этого куска"""


AGGREGATE_RECOMMENDATION_PREFIX = """Объедини рекомендации по фрагментам одного звонка в единый список.
Убери дубли, сгруппируй по темам (контакт, презентация, возражения, следующий шаг).

Фрагменты анализа:
---
"""

AGGREGATE_RECOMMENDATION_SUFFIX = """

---
Связный текст до 2000 слов."""


FINAL_RECOMMENDATION_PREFIX = """Ниже — сводка рекомендаций по всему звонку (после разбора по частям).
Сформируй итоговый ответ для менеджера: ободряющий тон, конкретика, с учётом этапа (секретарь vs ЛПР).

Сводка:
---
"""

FINAL_RECOMMENDATION_SUFFIX = "\n---"


@dataclass
class LongDialoguePipeline:
    """Сегментация → анализ блоков (RAG с коротким query) → агрегация → финал."""

    llm: Any
    retriever: Any

    @staticmethod
    def needs_chunked_processing(transcript: str) -> bool:
        if not transcript:
            return False
        limit = int(
            os.getenv("GIGACHAT_CHUNK_TRANSCRIPT_OVER_CHARS", str(TRANSCRIPT_CHAR_THRESHOLD))
        )
        return len(transcript.strip()) > limit

    @staticmethod
    def segment_transcript(
        text: str,
        max_len: int = SEGMENT_MAX_CHARS,
        overlap: int = SEGMENT_OVERLAP,
    ) -> list[str]:
        t = text.strip()
        if len(t) <= max_len:
            return [t]
        chunks: list[str] = []
        start = 0
        n = len(t)
        while start < n:
            end = min(start + max_len, n)
            if end < n:
                br = t.rfind("\n", start + max_len // 2, end)
                if br == -1:
                    br = t.rfind(" ", start + max_len // 2, end)
                if br != -1 and br > start:
                    end = br + 1
            piece = t[start:end].strip()
            if piece:
                chunks.append(piece)
            if end >= n:
                break
            start = max(start + 1, end - overlap)
        return chunks if chunks else [t]

    def _rag_context(self) -> str:
        docs = self.retriever.invoke(SHORT_RAG_QUERY)
        parts = [d.page_content for d in docs if getattr(d, "page_content", None)]
        return "\n\n---\n\n".join(parts) if parts else ""

    def _invoke_chat(self, system: str, human: str) -> str:
        """Без ChatPromptTemplate — в транскрипте могут быть символы {{ }}."""
        out = self.llm.invoke(
            [SystemMessage(content=system), HumanMessage(content=human)]
        )
        return extract_result(out)

    def run_resume(self, full_transcript: str) -> str:
        context = self._rag_context()
        segments = self.segment_transcript(full_transcript)
        total = len(segments)
        block_notes: list[str] = []

        for i, seg in enumerate(segments):
            human = (
                "Ты анализируешь ФРАГМЕНТ транскрипта телефонного звонка менеджера компании ГАРАНТ.\n"
                "Ниже — выдержки из внутренних документов (контекст компании). "
                "Используй их только если релевантны.\n\n"
                + context
                + f"\n\nФрагмент {i + 1} из {total}:\n---\n"
                + seg
                + "\n---\n\n"
                + BLOCK_RESUME_INSTRUCTIONS
            )
            text = self._invoke_chat(
                "Ты помощник для разметки транскриптов звонков.",
                human,
            )
            block_notes.append(f"=== Часть {i + 1}/{total} ===\n{text}")

        notes_joined = "\n\n".join(block_notes)
        aggregate_human = (
            AGGREGATE_RESUME_PREFIX + notes_joined + AGGREGATE_RESUME_SUFFIX
        )
        aggregated = self._invoke_chat(
            "Ты редактор деловых заметок.",
            aggregate_human,
        )

        system_full = RESUME_SYSTEM_PROMPT.format(context=context)
        final = self._invoke_chat(
            system_full,
            "Ниже объединённые заметки по звонку (транскрипт обработан по частям). "
            "Сформируй итоговое резюме строго по правилам системного сообщения.\n\n"
            + aggregated,
        )
        return final

    def run_recommendation(self, full_transcript: str) -> str:
        context = self._rag_context()
        segments = self.segment_transcript(full_transcript)
        total = len(segments)
        block_notes: list[str] = []

        for i, seg in enumerate(segments):
            human = (
                "Ты эксперт по продажам ИПО ГАРАНТ. Фрагмент транскрипта звонка.\n"
                "Контекст из документов:\n"
                + context
                + f"\n\nФрагмент {i + 1} из {total}:\n---\n"
                + seg
                + "\n---\n\n"
                + BLOCK_RECOMMENDATION_INSTRUCTIONS
            )
            text = self._invoke_chat("Ты коуч по продажам B2B.", human)
            block_notes.append(f"=== Часть {i + 1}/{total} ===\n{text}")

        notes_joined = "\n\n".join(block_notes)
        aggregate_human = (
            AGGREGATE_RECOMMENDATION_PREFIX
            + notes_joined
            + AGGREGATE_RECOMMENDATION_SUFFIX
        )
        aggregated = self._invoke_chat(
            "Ты редактор методических материалов.",
            aggregate_human,
        )

        system_full = RECOMMENDATION_SYSTEM_PROMPT.format(context=context)
        final_human = (
            FINAL_RECOMMENDATION_PREFIX + aggregated + FINAL_RECOMMENDATION_SUFFIX
        )
        final = self._invoke_chat(system_full, final_human)
        return final
