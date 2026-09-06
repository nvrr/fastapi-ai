import os
from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig
from fastapi.background import BackgroundTasks
from app.config.settings import get_settings

settings = get_settings()

conf = ConnectionConfig(
    MAIL_USERNAME=os.environ.get("MAIL_USERNAME", ""),
    MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD", ""),
    MAIL_PORT=os.environ.get("MAIL_PORT", 1025),
    MAIL_SERVER=os.environ.get("MAIL_SERVER", "localhost"),
    MAIL_STARTTLS=os.environ.get("MAIL_STARTTLS", False),
    MAIL_SSL_TLS=os.environ.get("MAIL_SSL_TLS", False),
    MAIL_DEBUG=True,
    MAIL_FROM=os.environ.get("MAIL_FROM", 'noreply@test.com'),
    MAIL_FROM_NAME=os.environ.get("MAIL_FROM_NAME", settings.APP_NAME),
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates",
    USE_CREDENTIALS=os.environ.get("USE_CREDENTIALS", False)
)

fm = FastMail(conf)


async def send_email(recipients: list, subject: str, context: dict, template_name: str,
                     background_tasks: BackgroundTasks):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        template_body=context,
        subtype=MessageType.html
    )

    background_tasks.add_task(fm.send_message, message, template_name=template_name)






# from typing import List

# from fastapi import FastAPI
# from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType, NameEmail
# from pydantic import BaseModel
# from starlette.responses import JSONResponse


# class EmailSchema(BaseModel):
#     email: List[NameEmail]


# conf = ConnectionConfig(
#     MAIL_USERNAME="username",
#     MAIL_PASSWORD="**********",
#     MAIL_FROM="test@email.com",
#     MAIL_PORT=465,
#     MAIL_SERVER="mail server",
#     MAIL_STARTTLS=False,
#     MAIL_SSL_TLS=True,
#     USE_CREDENTIALS=True,
#     VALIDATE_CERTS=True,
# )

# app = FastAPI()


# @app.post("/email")
# async def simple_send(email: EmailSchema) -> JSONResponse:
#     message = MessageSchema(
#         subject="Fastapi-Mail module",
#         recipients=email.model_dump().get("email"),
#         body="<p>Thanks for using Fastapi-mail</p>",
#         subtype=MessageType.html,
#     )
#     await FastMail(conf).send_message(message)
#     return JSONResponse(status_code=200, content={"message": "email has been sent"})

