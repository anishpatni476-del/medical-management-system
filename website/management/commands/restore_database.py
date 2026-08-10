import os
import requests

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Restore database from backup file"

    def add_arguments(self, parser):
        parser.add_argument(
            "backup_url",
            type=str,
            help="ImageKit backup URL"
        )

    def handle(self, *args, **options):

        backup_url = options["backup_url"]

        backup_file = "restore_backup.json"

        self.stdout.write(
            "Downloading backup..."
        )

        response = requests.get(backup_url)

        if response.status_code != 200:
            self.stdout.write(
                self.style.ERROR(
                    "Backup download failed"
                )
            )
            return

        with open(backup_file, "wb") as file:
            file.write(response.content)


        self.stdout.write(
            "Restoring database..."
        )

        call_command(
            "loaddata",
            backup_file
        )


        self.stdout.write(
            self.style.SUCCESS(
                "Database restored successfully"
            )
        )