from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField()
    includes = models.TextField(
        help_text="Enter one item per line."
    )

    # Pricing
    price_small = models.DecimalField(
        max_digits=7, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    price_medium = models.DecimalField(
        max_digits=7, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    price_large = models.DecimalField(
        max_digits=7, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    # Availability
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["price_small"]
        indexes = [
            models.Index(fields=["price_small"]),
            models.Index(fields=["is_active"]),
        ]
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.name

    @property
    def includes_list(self):
        """
        Convenience for templates: returns a cleaned list of 'includes' lines.
        """
        return [line.strip() for line in self.includes.splitlines() if line.strip()]
