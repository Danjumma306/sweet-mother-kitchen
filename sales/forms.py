"""Staff-facing forms for catalog management (not Django admin)."""

from django import forms

from .constants import MenuUnit
from .models import Category, MenuItem


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ("name", "category", "unit", "price", "is_active")
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "field-input",
                "placeholder": "Item name",
                "autocomplete": "off",
            }),
            "category": forms.Select(attrs={"class": "field-select"}),
            "unit": forms.Select(attrs={"class": "field-select"}),
            "price": forms.NumberInput(attrs={
                "class": "field-input",
                "min": "0",
                "step": "0.01",
            }),
            "is_active": forms.CheckboxInput(attrs={"style": "width:18px;height:18px;cursor:pointer;"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            unit_initial = self.instance.unit
        else:
            unit_initial = self.initial.get("unit", MenuUnit.PORTION)
        self.fields["unit"] = forms.ChoiceField(
            choices=MenuUnit.CHOICES,
            initial=unit_initial,
            widget=forms.Select(attrs={"class": "field-select"}),
        )
        self.fields["category"].queryset = Category.objects.order_by("name")
        self.fields["is_active"].label = "Available for sale"


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name",)
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "field-input",
                "placeholder": "Category name",
                "autocomplete": "off",
            }),
        }
