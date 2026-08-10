import os
import tempfile
from datetime import datetime
import json
from django.core.management.base import BaseCommand
from django.core.management import call_command

from imagekitio import ImageKit



class Command(BaseCommand):
    help = "Create database backup and upload to ImageKit"

    def handle(self, *args, **kwargs):

        filename = f"backup_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"

        # Temporary backup file
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".json"
        )

        temp_path = temp_file.name
        temp_file.close()


        # Create database backup
        with open(temp_path, "w", encoding="utf-8") as file:
            call_command(
                "dumpdata",
                stdout=file,
                indent=2
            )

            # Save backup details

        # Upload to ImageKit

        imagekit = ImageKit(
            private_key=os.environ.get("IMAGEKIT_PRIVATE_KEY")
        )


        with open(temp_path, "rb") as backup_file:

            response = imagekit.files.upload(
                file=backup_file,
                file_name=filename
            )

            # Delete old backups (keep latest 30)

            # Delete old backups (keep latest 30)



        # Delete temporary file

        os.remove(temp_path)


        self.stdout.write(
            self.style.SUCCESS(
                f"Backup uploaded successfully: {response.url}"
            )
        )