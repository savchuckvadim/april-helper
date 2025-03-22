FROM python:3.10.0


RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    g++ \
    gcc \
    libc6-dev \
    python3-dev \
    pkg-config \
    libopenblas-dev \
    liblapack-dev \
    libffi-dev \
    libpq-dev \
    libssl-dev \
    poppler-utils \
    libgl1-mesa-glx \
    libegl1-mesa \
    && rm -rf /var/lib/apt/lists/*
    
# Устанавливаем рабочую директорию
WORKDIR /var/www/html

# Копируем только файл requirements.txt в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir --default-timeout=100 -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# RUN pip install --no-cache-dir -r requirements.txt

# COPY database/db.sqlite3 /database/db.sqlite3

# RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]