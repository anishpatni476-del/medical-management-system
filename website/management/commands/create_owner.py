import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create owner superuser from environment variables"

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get("OWNER_USERNAME")
        password = os.environ.get("OWNER_PASSWORD")

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "OWNER_USERNAME or OWNER_PASSWORD is not set."
                )
            )
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.SUCCESS(
                    f"Owner '{username}' already exists."
                )
            )
            return

        User.objects.create_superuser(
            username=username,
            password=password
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Owner '{username}' created successfully."
            )
        )