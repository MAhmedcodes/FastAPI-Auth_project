import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config.config import settings


logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, html_body: str) -> None:
    """
    Sends an HTML email via SMTP.

    Args:
        to_email:  recipient's email address
        subject:   email subject line
        html_body: full HTML string for the email body
    """
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.EMAIL_USER
    message["To"] = to_email

    plain_text = (
        f"Congratulations! Your posts have received 1000+ votes. "
        f"Keep up the amazing work!"
    )

    part1 = MIMEText(plain_text, "plain")
    part2 = MIMEText(html_body, "html")

    message.attach(part1)
    message.attach(part2)

    try:

        with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:

            server.login(settings.EMAIL_USER, settings.EMAIL_PASS)
            server.sendmail(
                settings.EMAIL_USER,
                [to_email],
                message.as_string(),
            )

        logger.info(f"✅ Email successfully sent to {to_email}")

    except smtplib.SMTPAuthenticationError:
        logger.error("❌ SMTP Authentication failed. Check EMAIL_USERNAME and EMAIL_PASSWORD.")
        raise

    except smtplib.SMTPConnectError:
        logger.error("❌ Could not connect to SMTP server. Check EMAIL_HOST and EMAIL_PORT.")
        raise

    except Exception as e:
        logger.error(f"❌ Failed to send email to {to_email}: {e}", exc_info=True)
        raise