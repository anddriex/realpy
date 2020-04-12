import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_verification_email(username, code):
    response = None
    message = Mail(
        from_email='eamusikacha@gmail.com',
        to_emails=username,
        subject='Código de verificación',
        html_content=f'<p>Tu código de verificación es <strong>{code}</strong></p>')
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)

    return response
