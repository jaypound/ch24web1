# myapp/custom_smtp_backend.py
from django.core.mail.backends.smtp import EmailBackend

class DebugSMTPEmailBackend(EmailBackend):
    def open(self):
        result = super().open()
        if self.connection:
            # Set SMTP debug level to 1 to print detailed SMTP protocol exchanges
            self.connection.set_debuglevel(1)
        return result
