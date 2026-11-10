from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

ROLES = ["Cashier", "Manager", "Owner"]


class Command(BaseCommand):
    help = "Create the Cashier, Manager and Owner groups"

    def handle(self, *args, **options):
        for name in ROLES:
            _, created = Group.objects.get_or_create(name=name)
            status = "created" if created else "already exists"
            self.stdout.write(f"{name}: {status}")
        self.stdout.write(self.style.SUCCESS("Roles ready."))