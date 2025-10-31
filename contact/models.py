from django.db import models


class ContactMessage(models.Model):
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)  # optional
    first_name = models.CharField(max_length=35)
    last_name = models.CharField(max_length=35)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)  # oldest first
        indexes = [
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d} - {self.email} - {self.subject[:40]}"
