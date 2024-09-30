from django.core.management.base import BaseCommand
from studentpage.models import Candidate
from studentpage.utils import update_admission_number  # Changed this import
from django.db import transaction
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Updates all candidate admission numbers to the new format'

    def handle(self, *args, **options):
        initial_count = Candidate.objects.count()
        logger.info(f"Starting update process. Total candidates: {initial_count}")

        updated_count = 0
        unchanged_count = 0

        try:
            with transaction.atomic():
                for candidate in Candidate.objects.filter(admission_number__isnull=False):
                    new_number = update_admission_number(candidate.admission_number)
                    if new_number != candidate.admission_number:
                        candidate.admission_number = new_number
                        candidate.save(update_fields=['admission_number'])
                        updated_count += 1
                    else:
                        unchanged_count += 1

                final_count = Candidate.objects.count()
                if final_count != initial_count:
                    raise ValueError(f"Number of candidates changed from {initial_count} to {final_count}")

        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            self.stdout.write(self.style.ERROR('Update process failed. No changes were made.'))
            return

        logger.info(f"Update process completed. Updated: {updated_count}, Unchanged: {unchanged_count}")
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} admission numbers'))

        if unchanged_count > 0:
            self.stdout.write(
                self.style.WARNING(f'{unchanged_count} admission numbers were already in the correct format'))
