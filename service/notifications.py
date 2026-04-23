"""
Reminder notifications — email (SMTP) and SMS (Twilio).

Configure in service/.env:
  SMTP_HOST        = smtp.gmail.com
  SMTP_PORT        = 587
  SMTP_USER        = your@gmail.com
  SMTP_PASSWORD    = your_app_password
  FROM_EMAIL       = your@gmail.com        (defaults to SMTP_USER)
  FROM_NAME        = 1 Stop Medical Services

  TWILIO_ACCOUNT_SID = ACxxx...
  TWILIO_AUTH_TOKEN  = xxx...
  TWILIO_FROM_NUMBER = +12535550100

  APP_BASE_URL     = http://localhost:8020  (used in intake links)

If credentials are absent, channels are skipped and the call returns False.
"""
from __future__ import annotations
import os
import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

SMTP_HOST  = os.getenv("SMTP_HOST",  "smtp.gmail.com")
SMTP_PORT  = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER  = os.getenv("SMTP_USER",  "")
SMTP_PASS  = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)
FROM_NAME  = os.getenv("FROM_NAME",  "1 Stop Medical Services")

TWILIO_SID  = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_TOK  = os.getenv("TWILIO_AUTH_TOKEN",  "")
TWILIO_FROM = os.getenv("TWILIO_FROM_NUMBER", "")

APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8020")


def _appt_type_label(raw: str) -> str:
    return raw.replace("_", " ").title()


def _fmt_date(dt) -> str:
    if not dt:
        return "your upcoming appointment"
    try:
        return dt.strftime("%A, %b %-d at %-I:%M %p")
    except Exception:
        return str(dt)


# ── Email ─────────────────────────────────────────────────────────────────────

_EMAIL_HTML = """\
<div style="font-family:Arial,sans-serif;max-width:560px;margin:0 auto;padding:32px 24px;color:#1e2a38;background:#fff;border-radius:12px">
  <div style="margin-bottom:28px;padding-bottom:20px;border-bottom:1px solid #e8eff5">
    <span style="font-size:16px;font-weight:700;color:#1e2a38">1 Stop Medical Services</span>
    <span style="font-size:13px;color:#8a99aa;margin-left:8px">· Kent &amp; Bellevue, WA</span>
  </div>

  <h2 style="font-size:22px;font-weight:700;margin:0 0 6px;letter-spacing:-0.3px">
    Hi, {first_name}.
  </h2>
  <p style="font-size:15px;color:#5a6778;margin:0 0 24px;line-height:1.6">
    You have an upcoming <strong>{appt_type}</strong> on
    <strong>{appt_date}</strong>. Please complete your intake forms
    before your appointment.
  </p>

  <div style="background:#f0faf8;border:1px solid #c0e8e0;border-radius:10px;padding:18px 22px;margin-bottom:28px">
    <div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:#2a7a6a;margin-bottom:8px">
      📋 Intake forms status
    </div>
    <div style="display:flex;align-items:baseline;gap:8px">
      <span style="font-size:36px;font-weight:800;color:#186655">{forms_done}</span>
      <span style="font-size:16px;color:#4a8a80">/ {forms_total} completed</span>
    </div>
    <div style="margin-top:8px;background:#c0e8e0;border-radius:4px;height:6px">
      <div style="background:#2a9a80;height:100%;border-radius:4px;width:{pct}%"></div>
    </div>
    <div style="font-size:13.5px;color:#2a6a5a;font-weight:600;margin-top:10px">
      {remaining} form{remaining_s} still need{remaining_needs} to be completed.
    </div>
  </div>

  <a href="{intake_url}"
     style="display:inline-block;background:#2a7fd4;color:#fff;text-decoration:none;
            padding:13px 26px;border-radius:8px;font-weight:700;font-size:15px;
            letter-spacing:-0.2px;margin-bottom:28px">
    Complete my forms →
  </a>

  <p style="font-size:13px;color:#8a99aa;line-height:1.6;margin:0">
    Questions? Call us at <a href="tel:2533978683" style="color:#2a7fd4">(253) 397-8683</a>
    or reply to this email.<br/>
    1 Stop Medical Services · Kent &amp; Bellevue, WA
  </p>
</div>
"""


def send_reminder_email(
    to_email: str,
    patient_name: str,
    appt_type_raw: str,
    appt_date_str: str,
    forms_done: int,
    forms_total: int,
    intake_url: str,
) -> bool:
    first_name   = patient_name.split()[0]
    appt_type    = _appt_type_label(appt_type_raw)
    remaining    = forms_total - forms_done
    pct          = round(forms_done / forms_total * 100) if forms_total else 0
    remaining_s     = "s" if remaining != 1 else ""
    remaining_needs = "" if remaining != 1 else "s"

    if not SMTP_USER or not SMTP_PASS:
        print(f"[EMAIL] SMTP not configured — skipping reminder to {to_email}")
        print(f"[EMAIL] Message would say: {remaining} form{remaining_s} remaining before {appt_type} on {appt_date_str}")
        return False

    html = _EMAIL_HTML.format(
        first_name=first_name,
        appt_type=appt_type,
        appt_date=appt_date_str,
        forms_done=forms_done,
        forms_total=forms_total,
        pct=pct,
        remaining=remaining,
        remaining_s=remaining_s,
        remaining_needs=remaining_needs,
        intake_url=intake_url,
    )

    subject = f"Action needed: {remaining} intake form{remaining_s} remaining — {appt_type}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(html, "html"))

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls(context=ctx)
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(FROM_EMAIL, to_email, msg.as_string())
        print(f"[EMAIL] Reminder sent to {to_email}")
        return True
    except Exception as exc:
        print(f"[EMAIL] Failed to send to {to_email}: {exc}")
        return False


# ── SMS ───────────────────────────────────────────────────────────────────────

def send_reminder_sms(
    to_phone: str,
    patient_name: str,
    appt_type_raw: str,
    appt_date_str: str,
    forms_done: int,
    forms_total: int,
    intake_url: str,
) -> bool:
    first_name = patient_name.split()[0]
    appt_type  = _appt_type_label(appt_type_raw)
    remaining  = forms_total - forms_done
    remaining_s = "s" if remaining != 1 else ""

    body = (
        f"Hi {first_name}, this is 1 Stop Medical. "
        f"You have {remaining} intake form{remaining_s} remaining "
        f"({forms_done}/{forms_total} done) before your "
        f"{appt_type} on {appt_date_str}. "
        f"Complete them here: {intake_url}"
    )

    if not TWILIO_SID or not TWILIO_TOK or not TWILIO_FROM:
        print(f"[SMS] Twilio not configured — skipping reminder to {to_phone}")
        print(f"[SMS] Message would be: {body}")
        return False

    try:
        from twilio.rest import Client  # type: ignore
        client = Client(TWILIO_SID, TWILIO_TOK)
        message = client.messages.create(body=body, from_=TWILIO_FROM, to=to_phone)
        print(f"[SMS] Sent to {to_phone} — SID {message.sid}")
        return True
    except ImportError:
        print("[SMS] 'twilio' package not installed. Run: pip install twilio")
        return False
    except Exception as exc:
        print(f"[SMS] Failed to send to {to_phone}: {exc}")
        return False


# ── Unified send ──────────────────────────────────────────────────────────────

def send_reminder(
    patient_name: str,
    patient_email: Optional[str],
    patient_phone: Optional[str],
    appt_type_raw: str,
    appt_date,           # datetime or None
    forms_done: int,
    forms_total: int,
    intake_token: str,
) -> dict:
    appt_date_str = _fmt_date(appt_date)
    intake_url    = f"{APP_BASE_URL}/?t={intake_token}"

    email_sent = False
    sms_sent   = False

    if patient_email:
        email_sent = send_reminder_email(
            patient_email, patient_name, appt_type_raw,
            appt_date_str, forms_done, forms_total, intake_url,
        )
    if patient_phone:
        sms_sent = send_reminder_sms(
            patient_phone, patient_name, appt_type_raw,
            appt_date_str, forms_done, forms_total, intake_url,
        )

    remaining = forms_total - forms_done
    channels  = [c for c, ok in [("email", email_sent), ("SMS", sms_sent)] if ok]
    logged    = [c for c, has, ok in [("email", bool(patient_email), email_sent), ("SMS", bool(patient_phone), sms_sent)] if has and not ok]

    if channels:
        msg = f"Reminder sent via {' and '.join(channels)} — {remaining} form{'s' if remaining != 1 else ''} remaining."
    elif logged:
        msg = f"Reminder logged (delivery not configured for {', '.join(logged)})."
    else:
        msg = "No contact information on file — reminder not sent."

    return {
        "email_sent": email_sent,
        "sms_sent":   sms_sent,
        "remaining":  remaining,
        "message":    msg,
    }
