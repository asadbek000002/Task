import smtplib
from email.message import EmailMessage

import aiosmtplib

from core.settings import settings


async def send_verification_email(to_email: str, token: str):
    verify_url = f"{settings.BACKEND_URL}/api/v1/auth/verify-email?token={token}"

    msg = EmailMessage()
    msg["Subject"] = "Emailni tasdiqlash"
    msg["From"] = settings.SMTP_USER
    msg["To"] = to_email

    html_content = f"""
    <html>
      <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f9f9f9;">
        <table width="100%" height="100%" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td align="center" valign="top" style="padding: 20px;">
              <table width="100%" max-width="600px" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; padding: 40px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <tr>
                  <td align="center" style="padding-bottom: 20px;">
                    <h2 style="color: #333333; margin: 0;">Salom!</h2>
                  </td>
                </tr>
                <tr>
                  <td align="center" style="padding-bottom: 30px; color: #555555; font-size: 16px; line-height: 24px;">
                    Emailingizni tasdiqlash uchun quyidagi tugmani bosing:
                  </td>
                </tr>
                <tr>
                  <td align="center">
                    <a href="{verify_url}"
                       style="display: inline-block; padding: 15px 30px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">
                      Emailni tasdiqlash
                    </a>
                  </td>
                </tr>
                <tr>
                  <td align="center" style="padding-top: 30px; color: #777777; font-size: 14px; line-height: 20px;">
                    Agar bu siz bo‘lmasangiz, e’tibor bermang.
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

    msg.add_alternative(html_content, subtype="html")

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        start_tls=True,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
    )
