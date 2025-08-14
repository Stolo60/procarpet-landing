import os
import smtplib, ssl
from email.message import EmailMessage
from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))  # SSL by default
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
TO_EMAIL  = os.getenv("TO_EMAIL", SMTP_USER)

app = FastAPI()

# Serve static assets under /static
app.mount("/static", StaticFiles(directory="public"), name="static")

@app.get("/")
def home():
    return FileResponse("public/index.html")

@app.get("/favicon.ico")
def favicon():
    return FileResponse("public/favicon.ico")

# CORS (allow all for simplicity)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- No validation model --------
class Contact(BaseModel):
    # All fields optional and default to empty strings => no validation/restrictions
    name: Optional[str] = ""
    phone: Optional[str] = ""
    message: Optional[str] = ""
    lang: Optional[str] = "fr"

def send_email(subject: str, body: str):
    if not (SMTP_USER and SMTP_PASS and TO_EMAIL):
        raise RuntimeError("SMTP credentials or TO_EMAIL missing in environment variables.")
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = TO_EMAIL
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

@app.post("/api/contact")
async def contact(payload: Contact, request: Request):
    try:
        ip = request.client.host if request.client else "unknown"
        lang = (payload.lang or "fr").lower()[:2]
        name = payload.name or ""
        phone = payload.phone or ""
        message = payload.message or ""

        subject = "Nouveau message ProCarpet" if lang == "fr" else "New message — ProCarpet"
        body = (
            f"Lang: {lang}\n"
            f"From: {name}\n"
            f"Phone: {phone}\n"
            f"IP: {ip}\n\n"
            f"Message:\n{message}\n"
        )
        send_email(subject, body)
        return {"ok": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})
