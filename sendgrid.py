SENDGRID_API_KEY = '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'


def send_verification_email(username, code):
    status = f'send {code} via email here to {username}'
    print(status)
    return status
