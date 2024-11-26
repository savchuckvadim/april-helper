import pymorphy2


def genitive(word: str) -> str:
    if "__" in word:
        return word
    morph = pymorphy2.MorphAnalyzer(lang="ru")
    word = morph.parse(word)[0]
    print(word)
    word = word.inflect({"gent"})  # родительный
    print(f"Родительный падеж: {word.word}")

    return word.word


def to_fio_genitive(fio):
    morph = pymorphy2.MorphAnalyzer(lang="ru")
    parts = fio.split(" ")  # Разделяем ФИО на части
    genitive_parts = []

    for part in parts:
        if "__" in part:
            return fio
        parsed = morph.parse(part)[0]  # Получаем первую форму слова
        genitive_form = parsed.inflect({"gent"})  # Преобразуем в родительный падеж
        genitive_parts.append(genitive_form.word)

    # Объединяем обратно в строку и делаем первую букву каждого слова заглавной
    return " ".join(genitive_parts).title()


def to_position_genitive(position_director):
    morph = pymorphy2.MorphAnalyzer(lang="ru")
    parts = position_director.split(" ")  # Разделяем ФИО на части
    genitive_parts = []

    for part in parts:
        if "__" in part:
            return position_director
        parsed = morph.parse(part)[0]  # Получаем первую форму слова
        genitive_form = parsed.inflect({"gent"})  # Преобразуем в родительный падеж
        genitive_parts.append(genitive_form.word)

    # Объединяем обратно в строку и делаем первую букву каждого слова заглавной
    return " ".join(genitive_parts)


def format_fio(fio) -> str:
    # Разделяем строку на части (фамилия, имя, отчество)
    parts = fio.split()
    # Применяем title() к каждому элементу и объединяем обратно в строку
    formatted_fio = " ".join(part.title() for part in parts)
    return formatted_fio


def generated_declension_fio(fio_director: str):
    fio = ""
    for word in fio_director.split(" "):
        fio += genitive(word) + " "
    fio_format = fio[:-1]
    fio_format = format_fio(fio_director)
    return fio_format


# words = [
#     "дочь",
#     "девочка",
#     "дочка",
#     "абрикос",
#     "голубика",
#     "персик",
#     "овес",
#     "пшеница",
#     "рожь",
#     "груша",
#     "слива",
#     "яблоко",
#     "метелица",
#     "мороз",
#     "снег",
#     "тюльпан",
#     "резеда",
#     "гладиолус",
#     "весна",
#     "слякоть",
#     "оттепель",
#     "ягода",
#     "крыжовник",
#     "черника",
#     "сахар",
#     "конфета",
#     "мёд",
#     "сирень",
#     "акация",
#     "черёмуха",
#     "перец",
#     "корица",
#     "соль",
#     "лето",
#     "осень",
#     "зима",
#     "брошь",
#     "серьга",
#     "ожерелье",
#     "лицо",
#     "бровь",
#     "глаз",
#     "берёза",
#     "дуб",
#     "лён",
# ]
#
# words = [
#     "Иванов",
#     "Петров",
#     "Сидоров",
#     "Смирнов",
#     "Кузнецов",
#     "Попов",
#     "Васильев",
#     "Михайлов",
#     "Новиков",
#     "Федоров",
#     "Морозов",
#     "Волков",
#     "Соловьев",
#     "Павлов",
#     "Семенов",
#     "Белов",
#     "Григорьев",
#     "Ковалев",
#     "Степанов",
#     "Николаев",
# ]
# for word in words:
#     print(f"Слово: {word}")
#     declension(word)
