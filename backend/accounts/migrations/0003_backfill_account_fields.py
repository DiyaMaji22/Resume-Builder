"""
Backfills fields that Django added after the original service wrote its documents.

Documents written by the Node service have no ``is_active`` or ``is_staff``. Read through
Django they come back as None, which the login check treats as "inactive", so every
existing account would be locked out. This migration writes the same defaults a new
account gets. Matching ``{field: None}`` also matches a missing field in MongoDB.
"""

from django.db import migrations

DEFAULTS = {"is_active": True, "is_staff": False, "last_login": None}


def backfill_account_fields(apps, schema_editor):
    users = schema_editor.connection.get_collection("users")
    for field, value in DEFAULTS.items():
        users.update_many({field: None}, {"$set": {field: value}})


class Migration(migrations.Migration):
    dependencies = [("accounts", "0002_clear_legacy_refresh_tokens")]

    operations = [
        migrations.RunPython(backfill_account_fields, migrations.RunPython.noop),
    ]
