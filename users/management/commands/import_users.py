import csv
from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import CustomUser, Role
from django.db import transaction, connection


class Command(BaseCommand):
    help = 'Import users from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        self.stdout.write(self.style.SUCCESS(
            f'Starting import from {csv_file_path}'))

        # Track statistics
        created_count = 0
        updated_count = 0
        error_count = 0

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)

                # Use transaction to rollback if something goes wrong
                with transaction.atomic():
                    for row in reader:
                        try:
                            # Skip header row if present
                            if row[0] == "id" or not row:
                                continue

                            # Parse CSV data
                            id = int(row[0])
                            username = row[1]
                            email = row[2]
                            full_name = row[3]
                            password = row[4]  # Already hashed password
                            title = row[5]
                            last_name = row[6]
                            first_name = row[7]
                            allow_proxy = row[8] == "True"
                            voted_at = None if row[9] == "NULL" else row[9]
                            voted_longitude = None if row[10] == "NULL" else float(
                                row[10])
                            voted_latitude = None if row[11] == "NULL" else float(
                                row[11])
                            is_active = row[12] == "True"
                            is_verified = row[13] == "True"

                            # Get role
                            try:
                                role_id = int(row[14])
                                role = Role.objects.get(id=role_id)
                            except (ValueError, Role.DoesNotExist):
                                role = None

                            created_by = row[15]
                            updated_by = row[16]
                            created_at = timezone.now(
                            ) if row[17] == "NULL" else row[17]
                            updated_at = timezone.now(
                            ) if row[18] == "NULL" else row[18]
                            record_status_id = int(row[19])

                            # Check if user exists
                            user_exists = CustomUser.objects.filter(
                                id=id).exists()

                            if user_exists:
                                # Update existing user without messing with the password
                                user = CustomUser.objects.get(id=id)
                                user.username = username
                                user.email = email
                                user.full_name = full_name
                                user.title = title
                                user.last_name = last_name
                                user.first_name = first_name
                                user.allow_proxy = allow_proxy
                                user.voted_at = voted_at
                                user.voted_longitude = voted_longitude
                                user.voted_latitude = voted_latitude
                                user.is_active = is_active
                                user.is_verified = is_verified
                                user.role = role
                                user.created_by = created_by
                                user.updated_by = updated_by
                                user.created_at = created_at
                                user.updated_at = updated_at
                                user.record_status_id = record_status_id

                                if password:
                                    user.password = password

                                user.save(update_password=False)
                                updated_count += 1
                                self.stdout.write(f"Updated user: {username}")
                            else:
                                # Create new user
                                user = CustomUser(
                                    id=id,
                                    username=username,
                                    email=email,
                                    full_name=full_name,
                                    title=title,
                                    last_name=last_name,
                                    first_name=first_name,
                                    allow_proxy=allow_proxy,
                                    voted_at=voted_at,
                                    voted_longitude=voted_longitude,
                                    voted_latitude=voted_latitude,
                                    is_active=is_active,
                                    is_verified=is_verified,
                                    role=role,
                                    created_by=created_by,
                                    updated_by=updated_by,
                                    created_at=created_at,
                                    updated_at=updated_at,
                                    record_status_id=record_status_id
                                )

                                if password:
                                    user.password = password

                                user.save(update_password=False)
                                created_count += 1
                                self.stdout.write(f"Created user: {username}")

                        except Exception as e:
                            error_count += 1
                            self.stdout.write(self.style.ERROR(
                                f"Error processing row {row[0] if len(row) > 0 else 'unknown'}: {str(e)}"))
                            raise  # Re-raise to trigger the transaction rollback


            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT setval(pg_get_serial_sequence('users_customuser', 'id'), (SELECT MAX(id) FROM users_customuser))"
                )
                self.stdout.write(self.style.SUCCESS(
                    "PostgreSQL ID sequence synchronized."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f"Failed to import users: {str(e)}"))
            return

        self.stdout.write(self.style.SUCCESS(
            f'Import completed! Created: {created_count}, Updated: {updated_count}, Errors: {error_count}'))
