from sib_api_v3_sdk import Configuration, ApiClient, TransactionalEmailsApi, SendSmtpEmail
from django.conf import settings

def send_email_brevo(to_email, subject, html_content):
    config = Configuration()
    config.api_key['api-key'] = settings.BREVO_API_KEY
    api_instance = TransactionalEmailsApi(ApiClient(config))
    email = SendSmtpEmail(
        to=[{"email": to_email}],
        subject=subject,
        html_content=html_content,
        sender={"email": settings.DEFAULT_FROM_EMAIL, "name": "Finanças Pessoais"}
    )
    api_instance.send_transac_email(email)
