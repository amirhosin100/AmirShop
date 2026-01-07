FROM python:latest

LABEL author="amirhossein"
LABEL project_name="AmirShop"


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /src

COPY . /src

RUN pip install -U pip
RUN pip install -r requirements.txt

EXPOSE 8000


