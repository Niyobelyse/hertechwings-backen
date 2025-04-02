
from datetime import datetime
import random
import string
from django.core.mail import EmailMessage
from django.conf import settings

def sending_emails(send_to,body,sub):
    email = EmailMessage(
    sub,
    body,
    settings.EMAIL_HOST_USER,
    [send_to],
    )
    email.send()



def generate_otp():
    code = ''.join(random.choices(string.digits, k=6))
    return code
