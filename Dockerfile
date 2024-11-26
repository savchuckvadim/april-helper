FROM python:3.10.0

# Устанавливаем рабочую директорию
WORKDIR /var/www/html

# Копируем только файл requirements.txt в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# COPY database/db.sqlite3 /database/db.sqlite3

# RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]