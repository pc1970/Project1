"""
Notification module: SMS via Twilio, Email via smtplib.
Credentials are read from environment variables (see .env.example).
If credentials are missing, notifications are logged but not sent.
"""

import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt_phone(phone: str) -> str:
    """Ensure phone has a leading + for E.164 format (best-effort)."""
    if not phone:
        return phone
    digits = ''.join(c for c in phone if c.isdigit())
    if phone.startswith('+'):
        return phone
    if len(digits) == 10:          # US number without country code
        return f'+1{digits}'
    return f'+{digits}'


def _build_appointment_details(appt: dict) -> str:
    return (
        f"Appointment #{appt['id']}\n"
        f"Date: {appt['appointment_date']}  Time: {appt['appointment_time']}\n"
        f"Service: {appt.get('service_name', 'N/A')}\n"
        f"Stylist: {appt.get('staff_name', 'N/A')}\n"
        f"Status: {appt.get('status', 'scheduled').upper()}"
    )


# ---------------------------------------------------------------------------
# SMS via Twilio
# ---------------------------------------------------------------------------

def send_sms(to_phone: str, message: str) -> bool:
    """
    Send an SMS using Twilio.  Returns True on success, False otherwise.
    Required env vars: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER
    """
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID', '').strip()
    auth_token  = os.environ.get('TWILIO_AUTH_TOKEN', '').strip()
    from_number = os.environ.get('TWILIO_FROM_NUMBER', '').strip()

    if not all([account_sid, auth_token, from_number]):
        logger.warning('Twilio credentials not configured – SMS not sent to %s', to_phone)
        return False

    to_e164 = _fmt_phone(to_phone)
    if not to_e164:
        logger.warning('Invalid phone number: %s', to_phone)
        return False

    try:
        from twilio.rest import Client  # type: ignore
        client = Client(account_sid, auth_token)
        msg = client.messages.create(
            body=message,
            from_=from_number,
            to=to_e164,
        )
        logger.info('SMS sent: SID=%s to=%s', msg.sid, to_e164)
        return True
    except Exception as exc:
        logger.error('SMS send failed: %s', exc)
        return False


# ---------------------------------------------------------------------------
# Email via smtplib (works with Gmail, Outlook, any SMTP)
# ---------------------------------------------------------------------------

def send_email(to_email: str, subject: str, body_html: str, body_text: str = '') -> bool:
    """
    Send an email.  Returns True on success, False otherwise.
    Required env vars: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM
    Optional:          SMTP_USE_TLS (default '1'), SMTP_FROM_NAME
    """
    smtp_host     = os.environ.get('SMTP_HOST', '').strip()
    smtp_port     = int(os.environ.get('SMTP_PORT', '587'))
    smtp_user     = os.environ.get('SMTP_USER', '').strip()
    smtp_password = os.environ.get('SMTP_PASSWORD', '').strip()
    smtp_from     = os.environ.get('SMTP_FROM', smtp_user).strip()
    from_name     = os.environ.get('SMTP_FROM_NAME', 'Glamour Hair Salon').strip()
    use_tls       = os.environ.get('SMTP_USE_TLS', '1').strip() != '0'

    if not all([smtp_host, smtp_user, smtp_password]):
        logger.warning('SMTP credentials not configured – email not sent to %s', to_email)
        return False

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From']    = f'{from_name} <{smtp_from}>'
        msg['To']      = to_email

        if body_text:
            msg.attach(MIMEText(body_text, 'plain'))
        msg.attach(MIMEText(body_html, 'html'))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            if use_tls:
                server.starttls()
                server.ehlo()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_from, to_email, msg.as_string())

        logger.info('Email sent: subject="%s" to=%s', subject, to_email)
        return True
    except Exception as exc:
        logger.error('Email send failed: %s', exc)
        return False


# ---------------------------------------------------------------------------
# High-level notification builders
# ---------------------------------------------------------------------------

def _html_template(title: str, body: str, color: str = '#7c3aed') -> str:
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr><td align="center" style="padding:32px 16px;">
      <table width="560" cellpadding="0" cellspacing="0"
             style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.1);">
        <tr>
          <td style="background:{color};padding:24px 32px;color:#fff;">
            <h1 style="margin:0;font-size:22px;">✂ Glamour Hair Salon</h1>
            <p style="margin:4px 0 0;font-size:14px;opacity:.85;">{title}</p>
          </td>
        </tr>
        <tr>
          <td style="padding:28px 32px;color:#374151;font-size:15px;line-height:1.6;">
            {body}
          </td>
        </tr>
        <tr>
          <td style="padding:16px 32px;background:#f9fafb;color:#9ca3af;font-size:12px;text-align:center;">
            Glamour Hair Salon &bull; Call us: (555) 123-4567
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def notify_appointment_created(appt: dict) -> dict:
    """Send booking confirmation SMS + email. Returns {'sms': bool, 'email': bool}."""
    customer_name  = appt.get('customer_name', 'Valued Customer')
    service_name   = appt.get('service_name', 'your service')
    staff_name     = appt.get('staff_name', 'your stylist')
    appt_date      = appt.get('appointment_date', '')
    appt_time      = appt.get('appointment_time', '')
    customer_phone = appt.get('customer_phone', '')
    customer_email = appt.get('customer_email', '')
    price          = appt.get('price', '')

    # -- SMS --
    sms_body = (
        f"Hi {customer_name}! Your appointment at Glamour Hair Salon is CONFIRMED.\n"
        f"Service: {service_name}\n"
        f"Stylist: {staff_name}\n"
        f"Date/Time: {appt_date} at {appt_time}\n"
        f"Questions? Call (555) 123-4567. See you soon!"
    )
    sms_ok = send_sms(customer_phone, sms_body) if customer_phone else False

    # -- Email --
    price_row = f'<tr><td><b>Price:</b></td><td>${price:.2f}</td></tr>' if price else ''
    html_body = f"""
        <p>Hi <b>{customer_name}</b>,</p>
        <p>Your appointment has been <b style="color:#7c3aed;">confirmed</b>. Here are your details:</p>
        <table cellpadding="6" style="border-collapse:collapse;width:100%;">
          <tr><td><b>Service:</b></td><td>{service_name}</td></tr>
          <tr><td><b>Stylist:</b></td><td>{staff_name}</td></tr>
          <tr><td><b>Date:</b></td><td>{appt_date}</td></tr>
          <tr><td><b>Time:</b></td><td>{appt_time}</td></tr>
          {price_row}
        </table>
        <p style="margin-top:20px;">Need to reschedule? Call us at <a href="tel:5551234567">(555) 123-4567</a>
        or reply to this email.</p>
        <p>We look forward to seeing you!</p>
    """
    email_ok = send_email(
        customer_email,
        f'Appointment Confirmed – {appt_date} at {appt_time}',
        _html_template('Booking Confirmation', html_body),
        _build_appointment_details(appt),
    ) if customer_email else False

    return {'sms': sms_ok, 'email': email_ok}


def notify_appointment_cancelled(appt: dict) -> dict:
    """Send cancellation SMS + email."""
    customer_name  = appt.get('customer_name', 'Valued Customer')
    service_name   = appt.get('service_name', 'your service')
    appt_date      = appt.get('appointment_date', '')
    appt_time      = appt.get('appointment_time', '')
    customer_phone = appt.get('customer_phone', '')
    customer_email = appt.get('customer_email', '')

    sms_body = (
        f"Hi {customer_name}, your Glamour Hair Salon appointment "
        f"({service_name} on {appt_date} at {appt_time}) has been CANCELLED. "
        f"To rebook, call (555) 123-4567."
    )
    sms_ok = send_sms(customer_phone, sms_body) if customer_phone else False

    html_body = f"""
        <p>Hi <b>{customer_name}</b>,</p>
        <p>We're writing to let you know that your appointment has been <b style="color:#dc2626;">cancelled</b>.</p>
        <table cellpadding="6" style="border-collapse:collapse;width:100%;">
          <tr><td><b>Service:</b></td><td>{service_name}</td></tr>
          <tr><td><b>Date:</b></td><td>{appt_date}</td></tr>
          <tr><td><b>Time:</b></td><td>{appt_time}</td></tr>
        </table>
        <p style="margin-top:20px;">We'd love to reschedule! Call us at
        <a href="tel:5551234567">(555) 123-4567</a>.</p>
    """
    email_ok = send_email(
        customer_email,
        f'Appointment Cancelled – {appt_date} at {appt_time}',
        _html_template('Appointment Cancelled', html_body, color='#dc2626'),
        _build_appointment_details(appt),
    ) if customer_email else False

    return {'sms': sms_ok, 'email': email_ok}


def notify_appointment_reminder(appt: dict) -> dict:
    """Send reminder SMS + email (call 24 h before appointment)."""
    customer_name  = appt.get('customer_name', 'Valued Customer')
    service_name   = appt.get('service_name', 'your service')
    staff_name     = appt.get('staff_name', 'your stylist')
    appt_date      = appt.get('appointment_date', '')
    appt_time      = appt.get('appointment_time', '')
    customer_phone = appt.get('customer_phone', '')
    customer_email = appt.get('customer_email', '')

    sms_body = (
        f"Reminder: Hi {customer_name}! You have an appointment TOMORROW at Glamour Hair Salon.\n"
        f"{service_name} with {staff_name} at {appt_time}.\n"
        f"To cancel/reschedule call (555) 123-4567."
    )
    sms_ok = send_sms(customer_phone, sms_body) if customer_phone else False

    html_body = f"""
        <p>Hi <b>{customer_name}</b>,</p>
        <p>Just a friendly reminder that your appointment is <b>tomorrow</b>!</p>
        <table cellpadding="6" style="border-collapse:collapse;width:100%;">
          <tr><td><b>Service:</b></td><td>{service_name}</td></tr>
          <tr><td><b>Stylist:</b></td><td>{staff_name}</td></tr>
          <tr><td><b>Date:</b></td><td>{appt_date}</td></tr>
          <tr><td><b>Time:</b></td><td>{appt_time}</td></tr>
        </table>
        <p style="margin-top:20px;">Need to cancel or reschedule? Please call us at least 24 hours in advance:
        <a href="tel:5551234567">(555) 123-4567</a>.</p>
        <p>See you soon!</p>
    """
    email_ok = send_email(
        customer_email,
        f'Reminder: Your appointment is tomorrow at {appt_time}',
        _html_template('Appointment Reminder', html_body, color='#0891b2'),
        _build_appointment_details(appt),
    ) if customer_email else False

    return {'sms': sms_ok, 'email': email_ok}
