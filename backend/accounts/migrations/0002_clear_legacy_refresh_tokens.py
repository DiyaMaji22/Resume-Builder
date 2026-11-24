"""
Clears refresh-token entries written by the original Node.js service.

Those were bcrypt hashes of JWTs. The new service stores token IDs (JTIs), so the old
entries can never match and would only occupy session slots. Users sign in again once.
"""

from django.db import migrations


def clear_legacy_refresh_tokens(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.update(refresh_token_ids=[])


class Migration(migrations.Migration):
    dependencies = [("accounts", "0001_initial")]

    operations = [
        migrations.RunPython(clear_legacy_refresh_tokens, migrations.RunPython.noop),
    ]
