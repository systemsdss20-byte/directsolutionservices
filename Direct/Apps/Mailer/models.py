from django.db import models

# Create your models here.

class EmailQueue(models.Model):
    to = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Queued Email'
        verbose_name_plural = 'Queued Emails'
        ordering = ['-created_at']

    def __str__(self):
        return f"To: {self.to} | Subject: {self.subject} | Sent: {self.sent}"
