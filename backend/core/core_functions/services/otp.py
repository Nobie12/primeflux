import secrets

import africastalking
import resend
from django.conf import settings

from core.core_functions.services.cache.redis_client import RedisClient

# Initialize AT
africastalking.initialize(getattr(settings, "AT_USERNAME", "sandbox"), getattr(settings, "AT_API_KEY", ""))
sms = africastalking.SMS


class OTPService:
    @staticmethod
    def generate_otp(length=6):
        """Generates a random OTP of the specified length."""
        return "".join(str(secrets.randbelow(10)) for _ in range(length))

    @staticmethod
    def send_otp(phone):
        """sends OTP to the specified phone number."""
        client = RedisClient()
        otp_key = f"otp:{phone}"
        cooldown_key = f"otp_cooldown:{phone}"

        ttl = client.get_ttl(cooldown_key)
        if ttl > 0:
            minutes, seconds = divmod(ttl, 60)
            return False, f"Please wait {minutes}m {seconds}s before resending."

        otp = OTPService.generate_otp()

        # Format for Africa's Talking (+254...)
        at_phone = f"+254{phone[1:]}"  # Converts 07.../ 01... to +2547...

        try:
            message = f"Your Primeflux verification code is: {otp}. Valid for 5 minutes."
            sms.send(message, [at_phone])
            client.set(otp_key, otp, ex=300)  # OTP valid for 5 minutes
            client.set(cooldown_key, "locked", ex=120)  # Cooldown of 2 minutes
            return True, "OTP sent successfully."
        except Exception as e:
            return False, f"Failed to send OTP: {str(e)}"

    @staticmethod
    def verify_otp(phone, input_otp):
        """Verifies the provided OTP against the stored value."""
        client = RedisClient()
        otp_key = f"otp:{phone}"
        attempts_key = f"otp_attempts:{phone}"

        attempts = int(client.get(attempts_key) or "0")

        if attempts >= 5:
            ttl = client.get_ttl(attempts_key)
            minutes, seconds = divmod(ttl, 60)
            return False, f"Too many failed attempts. Try again in {minutes}m {seconds}s."

        stored_otp = client.get(otp_key)

        if stored_otp is None:
            return False, "OTP expired or not found."

        if str(stored_otp) == str(input_otp):
            client.delete(otp_key)  # Invalidate OTP after successful verification
            client.delete(attempts_key)  # Reset attempts on success
            return True, "OTP verified successfully."

        attempts = client.incr(attempts_key)
        if attempts == 1:
            client.set_ttl(attempts_key, 600)  # Lockout for 10 minutes after first failed attempt

        remaining_attempts = 5 - attempts
        if remaining_attempts > 0:
            return False, f"Invalid OTP. {remaining_attempts} attempts remaining."

        return (False, "Too many failed attempts. Try again in 10 minutes.")

    @staticmethod
    def send_email_otp(email):
        """Sends OTP to the specific email"""
        client = RedisClient()
        otp_key = f"otp:{email}"
        cooldown_key = f"cooldown:{email}"

        otp = OTPService.generate_otp(6)

        ttl = client.get_ttl(cooldown_key)
        if ttl > 0:
            minutes, seconds = divmod(ttl, 60)
            return False, f"Please wait {minutes}m {seconds}s before resending."

        try:
            resend.api_key = settings.RESEND_API_KEY

            params: resend.Emails.SendParams = {
                "from": settings.DEFAULT_FROM_EMAIL,
                "to": [email],
                "subject": "Primeflux | Verify your Email",
                "html": f"<strong>Your verification code is: {otp}</strong>",
            }

            resend.Emails.send(params)
            client.set(otp_key, otp, ex=600)
            client.set(cooldown_key, "locked", ex=60)
            return True, "OTP sent successfully."

        except Exception as e:
            return False, f"Failed to send OTP: {str(e)}"

    @staticmethod
    def verify_email_otp(email, otp_input):
        client = RedisClient()
        otp_key = f"otp:{email}"
        attempts_key = f"otp_attempts:{email}"

        attempts = int(client.get(attempts_key) or "0")
        # Check if user is currently locked out
        if attempts >= 5:
            ttl = client.get_ttl(attempts_key)
            minutes, seconds = divmod(ttl, 60)

            return (False, f"Too many failed attempts. Try again in {minutes}m {seconds}s.")

        stored_otp = client.get(otp_key)
        if stored_otp is None:
            return False, "OTP expired or not found."

        if str(stored_otp) == str(otp_input):
            client.delete(otp_key)
            client.delete(attempts_key)
            return True, "OTP verified successfully."

        attempts = client.incr(attempts_key)
        # First failed attempt starts the lockout timer
        if attempts == 1:
            client.set_ttl(attempts_key, 600)

        remaining_attempts = 5 - attempts
        if remaining_attempts <= 0:
            client.delete(otp_key)
            return (False, "Too many failed attempts. OTP invalidated. Request a new OTP.")

        return (False, "Too many failed attempts. Try again in 10 minutes.")
