"""
Do stuff with e-mails
"""

def send_email(to_email, subject, html_msg, date):
    """
    Send e-mail to some destination
    """

    import smtplib, ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from glass.firecons.email import con_email

    ep = con_email()

    HOST     = ep["HOST"]
    USER     = ep["USER"]
    PASSWORD = ep["PASSWORD"]
    PORT     = ep["PORT"]

    # Create message
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = USER
    message["To"] = to_email
    message["Date"] = date

    # Turn these into plain/html MIMEText objects
    textmessage = MIMEText(html_msg, 'html')

    # Add HTML part to MIMEmultipart message
    message.attach(textmessage)

    ctx = ssl.create_default_context()

    with smtplib.SMTP(HOST, int(PORT)) as server:
        server.ehlo()
        server.starttls(context=ctx)

        try:
            server.login(USER, PASSWORD)
        except:
            return -1
        
        try:
            server.sendmail(USER, to_email, message.as_string())
        except:
            return 0
        
        server.quit()
        
        return 1

