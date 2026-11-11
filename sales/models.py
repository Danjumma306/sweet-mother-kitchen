from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="items")
    unit = models.CharField(max_length=20, default="portion")  # piece, portion, ball
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.unit})"


class Sale(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = "CASH", "Cash"
        MOMO = "MOMO", "Mobile Money"
        CARD = "CARD", "Card"

    class Status(models.TextChoices):
        COMPLETED = "COMPLETED", "Completed"
        VOIDED = "VOIDED", "Voided"

    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    cashier = models.ForeignKey(User, on_delete=models.PROTECT, related_name="sales")
    payment_method = models.CharField(max_length=10, choices=PaymentMethod.choices)
    discount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.COMPLETED)
    void_reason = models.CharField(max_length=200, blank=True)
    approved_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True, related_name="approved_sales"
    )  # manager who approved a void or discount

    @property
    def gross_total(self):
        return sum(line.line_total for line in self.lines.all())

    @property
    def net_total(self):
        return self.gross_total - self.discount

    def __str__(self):
        return f"Sale #{self.pk} - {self.date}"


class SaleLine(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="lines")
    item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)  # price at time of sale

    @property
    def line_total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"
 

class KitchenEntry(models.Model):
    date = models.DateField()
    item = models.ForeignKey(MenuItem, on_delete=models.PROTECT, related_name="kitchen_entries")
    quantity_prepared = models.PositiveIntegerField()
    recorded_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="kitchen_entries")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("date", "item")

    def __str__(self):
        return f"{self.date}: {self.quantity_prepared} x {self.item.name}"

class ClosingEntry(models.Model):
    date = models.DateField()
    item = models.ForeignKey(MenuItem, on_delete=models.PROTECT, related_name="closing_entries")
    quantity_left = models.PositiveIntegerField(default=0)
    sold_out = models.BooleanField(default=False)
    recorded_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="closing_entries")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("date", "item")

    def __str__(self):
        return f"{self.date}: {self.quantity_left} left of {self.item.name}"


class CashCount(models.Model):
    date = models.DateField(unique=True)
    cash_counted = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=200, blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="cash_counts")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date}: GH₵ {self.cash_counted}"