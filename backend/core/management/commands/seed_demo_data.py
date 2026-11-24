from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from accounts.models import User
from core.demo_data import DEMO_PASSWORD, seed_demo_data
from resumes.models import Resume


class Command(BaseCommand):
    help = f"Populate the database with demo users (password: {DEMO_PASSWORD!r}) and resumes."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("--flush", action="store_true", help="Delete existing users and resumes first.")
        parser.add_argument("--force", action="store_true", help="Allow running with DEBUG disabled.")

    def handle(self, *args: Any, **options: Any) -> None:
        if not settings.DEBUG and not options["force"]:
            raise CommandError(
                "Refusing to seed demo data with DEBUG disabled. Pass --force if this is intended."
            )
        if not options["flush"] and (User.objects.exists() or Resume.objects.exists()):
            raise CommandError("The database is not empty. Pass --flush to replace its contents.")

        counts = seed_demo_data(flush=options["flush"])
        self.stdout.write(
            self.style.SUCCESS(f"Seeded {counts['users']} users and {counts['resumes']} resumes.")
        )
