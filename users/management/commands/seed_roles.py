from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import Role

class Command(BaseCommand):
    help = 'Seeds the database with predefined roles'

    def handle(self, *args, **kwargs):
        roles_data = [
            {
                "id": 1,
                "role_name": "Administrator",
                "role_level": 8,
                "description": "Systems Administrator",
                "notes": "Systems Administrator",
                "created_by": "system",
                "updated_by": "system",
                "created_at": timezone.now(),
                "updated_at": timezone.now(),
                "record_status_id": 1
            },
            {
                "id": 2,
                "role_name": "Elecom",
                "role_level": 7,
                "description": "Election Committee",
                "notes": "Election Committee",
                "created_by": "system",
                "updated_by": "system",
                "created_at": timezone.now(),
                "updated_at": timezone.now(),
                "record_status_id": 1
            },
            {
                "id": 3,
                "role_name": "Member",
                "role_level": 2,
                "description": "Member",
                "notes": "Member",
                "created_by": "system",
                "updated_by": "system",
                "created_at": timezone.now(),
                "updated_at": timezone.now(),
                "record_status_id": 1
            },
            {
                "id": 4,
                "role_name": "BoT",
                "role_level": 7,
                "description": "Board of Trustee",
                "notes": "Member of the Board of Trustees",
                "created_by": "system",
                "updated_by": "system",
                "created_at": timezone.now(),
                "updated_at": timezone.now(),
                "record_status_id": 1
            },
            {
                "id": 5,
                "role_name": "Candidate",
                "role_level": 7,
                "description": "Candidate",
                "notes": "Candidate for the New Board of Trustees",
                "created_by": "system",
                "updated_by": "system",
                "created_at": timezone.now(),
                "updated_at": timezone.now(),
                "record_status_id": 1
            },
            {
                "id": 6,
                "role_name": "BoT and Candidate",
                "role_level": 7,
                "description": "BoT and Candidate",
                "notes": "Current BoT and Candidate for the New Board of Trustees",
                "created_by": "system",
                "updated_by": "system",
                "created_at": timezone.now(),
                "updated_at": timezone.now(),
                "record_status_id": 1
            }
        ]

        # Clear existing roles if needed
        # Role.objects.all().delete()

        for role_data in roles_data:
            role, created = Role.objects.update_or_create(
                id=role_data["id"],
                defaults={
                    "role_name": role_data["role_name"],
                    "role_level": role_data["role_level"],
                    "description": role_data["description"],
                    "notes": role_data["notes"],
                    "created_by": role_data["created_by"],
                    "updated_by": role_data["updated_by"],
                    "created_at": role_data["created_at"],
                    "updated_at": role_data["updated_at"],
                    "record_status_id": role_data["record_status_id"]
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created role: {role.role_name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Updated role: {role.role_name}'))