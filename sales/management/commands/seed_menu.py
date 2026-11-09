from django.core.management.base import BaseCommand
from sales.models import Category, MenuItem

# (name, category, unit, price) - test data only, prices are made up
MENU = [
    # Swallow
    ("Fufu", "Swallow", "ball", "15.00"),
    ("Banku", "Swallow", "ball", "10.00"),
    ("Kenkey", "Swallow", "ball", "8.00"),
    ("Omo Tuo", "Swallow", "ball", "12.00"),
    # Meat and fish
    ("Goat Meat", "Meat", "piece", "10.00"),
    ("Chicken", "Meat", "piece", "20.00"),
    ("Beef", "Meat", "piece", "8.00"),
    ("Tilapia", "Fish", "piece", "25.00"),
    # Soup and stew
    ("Light Soup", "Soup", "bowl", "10.00"),
    ("Groundnut Soup", "Soup", "bowl", "12.00"),
    # Rice dishes
    ("Jollof Rice", "Rice", "plate", "25.00"),
    ("Waakye", "Rice", "plate", "20.00"),
    # Drinks
    ("Bottled Water", "Drinks", "bottle", "3.00"),
    ("Soft Drink", "Drinks", "bottle", "6.00"),
]


class Command(BaseCommand):
    help = "Fill the database with test categories and menu items"

    def handle(self, *args, **options):
        created = 0
        for name, category_name, unit, price in MENU:
            category, _ = Category.objects.get_or_create(name=category_name)
            _, was_created = MenuItem.objects.update_or_create(
                name=name,
                defaults={"category": category, "unit": unit, "price": price},
            )
            created += was_created
        self.stdout.write(self.style.SUCCESS(
            f"Menu ready: {created} new items, {len(MENU) - created} updated."
        ))