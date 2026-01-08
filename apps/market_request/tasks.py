import time
from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_mail_to_owner_request(email, name):
    time.sleep(10)

    message = (
        f'Hi {name} :'
        'Your market request has been sent '
        'And accepted by Admin'
        'Now you can make your markets and products'
        'Thanks. AmirShop team'
    )
    print('sending message:')
    print(f'{email} : {message}')
