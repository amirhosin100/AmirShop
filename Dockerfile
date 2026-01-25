FROM python:latest

LABEL author="amirhossein"
LABEL project_name="AmirShop"


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /src

COPY . /src

RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt

RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

EXPOSE 8000


