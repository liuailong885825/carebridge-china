"""
Vercel serverless function — receives chat form submissions and forwards to QQ email.
"""
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from http.server import BaseHTTPRequestHandler

QQ_EMAIL = os.environ.get("QQ_EMAIL", "15034029676@qq.com")
RECIPIENTS = [
    "15034029676@qq.com",
    "shanxizuoquanmaoti@qq.com",
]
QQ_SMTP_AUTH = os.environ.get("QQ_SMTP_AUTH", "")
QQ_SMTP_HOST = "smtp.qq.com"
QQ_SMTP_PORT = 465


def send_email(phone: str, email: str = "") -> bool:
    if not QQ_SMTP_AUTH:
        print("QQ_SMTP_AUTH not set — skipping email send")
        return False

    subject = "New Patient Inquiry — CareBridge China"
    body = f"""New lead from CareBridge China website:

Phone: {phone}
Email: {email or 'not provided'}

---
Reply to this lead directly.
"""

    msg = MIMEMultipart()
    msg["From"] = QQ_EMAIL
    msg["To"] = ", ".join(RECIPIENTS)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        server = smtplib.SMTP_SSL(QQ_SMTP_HOST, QQ_SMTP_PORT, timeout=10)
        server.login(QQ_EMAIL, QQ_SMTP_AUTH)
        server.sendmail(QQ_EMAIL, RECIPIENTS, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)

            phone = data.get("phone", "").strip()
            email = data.get("email", "").strip()

            if not phone:
                self._respond(400, {"ok": False, "error": "Phone required"})
                return

            success = send_email(phone, email)
            self._respond(200, {"ok": True, "sent": success})

        except Exception as e:
            self._respond(500, {"ok": False, "error": str(e)})

    def _respond(self, status: int, body: dict):
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode("utf-8"))
