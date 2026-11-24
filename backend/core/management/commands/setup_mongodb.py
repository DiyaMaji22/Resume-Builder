from typing import Any

from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS, connections

from core.mongodb import VALIDATORS, ensure_indexes, install_validator


class Command(BaseCommand):
    help = "Install $jsonSchema validators and required indexes. Safe to run repeatedly."

    def handle(self, *args: Any, **options: Any) -> None:
        database = connections[DEFAULT_DB_ALIAS].get_database()
        for collection, validator in VALIDATORS.items():
            outcome = install_validator(database, collection, validator)
            self.stdout.write(self.style.SUCCESS(f"{outcome.capitalize()} validator on '{collection}'."))
        for index in ensure_indexes(database):
            self.stdout.write(self.style.SUCCESS(f"Created index {index}."))
