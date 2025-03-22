from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.modules.ai.services.chroma_service import ChromaService
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from src.modules.ai.model.prompts import (
    RESUME_SYSTEM_PROMPT,
    RECOMMENDATION_SYSTEM_PROMPT,
    CONTEXTUALIZE_PROMPT,
)


class LLMBase:
    @staticmethod
    def get_retriver(embeddings, embedding_id: str):
      
        retriever = ChromaService.get_vectorstore(embeddings, embedding_id).as_retriever(search_kwargs={"k": 2})

        return retriever

    @staticmethod
    def resume_prompt(with_history: bool = False):
        system_text = RESUME_SYSTEM_PROMPT
        messages = [("system", system_text)]

        if with_history:
            messages.append(MessagesPlaceholder("chat_history"))

        messages.append(("human", "{input}"))

        return ChatPromptTemplate.from_messages(messages)

    @staticmethod
    def recomendation_prompt(with_history: bool = False):
        system_text = RECOMMENDATION_SYSTEM_PROMPT

        messages = [("system", system_text)]

        if with_history:
            messages.append(MessagesPlaceholder("chat_history"))

        messages.append(("human", "{input}"))

    @staticmethod
    def contextualize_prompt():
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    CONTEXTUALIZE_PROMPT,
                ),
                MessagesPlaceholder("chat_history"),
                ("user", "{input}"),
            ]
        ).partial(context="{context}")

    @staticmethod
    def build_chain(llm, retriever, with_history: bool = False):
        if with_history:
            history_prompt = LLMBase.contextualize_prompt()
            qa_prompt = LLMBase.recomendation_prompt()

            history_aware_retriever = create_history_aware_retriever(
                llm, retriever, history_prompt
            )
            document_chain = create_stuff_documents_chain(llm, qa_prompt)
            return create_retrieval_chain(history_aware_retriever, document_chain)

        # Без учёта истории
        qa_prompt = LLMBase.recomendation_prompt()
        document_chain = create_stuff_documents_chain(llm, qa_prompt)
        return create_retrieval_chain(retriever, document_chain)

    @staticmethod
    def build_resume_chain(llm, retriever, with_history: bool = False):
        prompt = LLMBase.resume_prompt(with_history)
        document_chain = create_stuff_documents_chain(llm, prompt)
        return create_retrieval_chain(retriever, document_chain)
