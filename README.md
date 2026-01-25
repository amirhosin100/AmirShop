# AmirShop project

This is a shopping API project.
Make by Django and DjangoRESTFramework.


## run project

#### Step 1 : Make a .env file or 

```shell
cp .env.example .env
```

#### Step 2 : Run this command. (Make sure to install Docker.)
```
docker compose up --build
```

## Project schema

```text
.
├── apps
│   ├── cart
│   ├── market
│   ├── market_request
│   ├── product
│   ├── transaction
│   ├── user
│   └── __init__.py
├── base
│   ├── base_admin.py
│   ├── base_models.py
│   └── __init__.py
├── config
│   ├── asgi.py
│   ├── wsgi.py
│   ├── settings.py
│   ├── urls.py
│   └── __init__.py
├── Dockerfile
├── manage.py
├── media
├── permissions
│   ├── __init__.py
│   ├── market.py
│   ├── product.py
│   └── tests
├── README.md
├── requirements.txt
└── utils
    ├── validate.py
    ├── tests
    └── __init__.py

```