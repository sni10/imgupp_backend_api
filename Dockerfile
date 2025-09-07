# Использовать официальный образ Miniconda
FROM continuumio/miniconda3

# Установить необходимые системные пакеты
RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev-compat \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Установить рабочую директорию
WORKDIR /imgupp_root

# Копировать файл requirements.txt
COPY requirements.txt /imgupp_root/

# Создать и активировать новое окружение conda
RUN conda create -n img_upp_project python=3.10 -y && \
    echo "source activate img_upp_project" > ~/.bashrc


# Установить переменную окружения, чтобы оболочка активировала окружение при запуске
ENV PATH /opt/conda/envs/img_upp_project/bin:$PATH

# Установить зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копировать проект
COPY . /imgupp_root/

# Установить порт, который будет прослушиваться во время разработки
EXPOSE 8000

# Запуск приложения Django через manage.py
#CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]

CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8000", "imgupp_root.wsgi:application"]
