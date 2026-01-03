FROM python:latest

LABEL author="amirhossein"
LABEL project_name="AmirShop"

WORKDIR /src

COPY . /src


RUN pip install -r requirements.txt

CMD ["python" ,"manage.py" ,"runserver","0.0.0.0:8000"]


