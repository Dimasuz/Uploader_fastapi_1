# from celery import Celery, shared_task
#
# from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
# import schema
# from config import MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM, MAIL_PORT, MAIL_SERVER, MAIL_SSL_TLS
#
#
# CELERY_BROKER_URL = 'redis://localhost:6378/0'
# CELERY_RESULT_BACKEND = 'redis://localhost:6378/0'
#
# client = Celery('app',
#              broker=CELERY_BROKER_URL,
#              backend=CELERY_RESULT_BACKEND,
#              # include=['app.tasks']
#                 )
#
# # Optional configuration, see the application user guide.
# client.conf.update(
#     result_expires=3600,
# )
#
#
# @client.task
# def send_mail(email: schema.EmailSchema) -> dict:
#     conf = ConnectionConfig(
#         MAIL_USERNAME=MAIL_USERNAME,
#         MAIL_PASSWORD=MAIL_PASSWORD,
#         MAIL_FROM=MAIL_FROM,
#         MAIL_PORT=MAIL_PORT,
#         MAIL_SERVER=MAIL_SERVER,
#         MAIL_STARTTLS=False,
#         MAIL_SSL_TLS=MAIL_SSL_TLS,
#         USE_CREDENTIALS=True,
#         VALIDATE_CERTS=True,
#     )
#     html = """
#     <p>Thanks for using Uploader</p>
#     """
#     message = MessageSchema(
#         subject=email.subject,
#         recipients=email.email,
#         body=email.massage,
#         subtype=MessageType.html
#     )
#     fm = FastMail(conf)
#     fm.send_message(message)
#     return None
#
#
# if __name__ == '__main__':
#     client.start()
