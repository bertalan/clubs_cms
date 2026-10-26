"""
One credential per direction instead of one pair shared by both sites.

The existing pair becomes the access we issued (inbound) and is also copied
to the access the partner issued us (outbound), so a link that worked keeps
working until one side creates new values.
"""

from django.db import migrations, models

from apps.federation.utils import generate_public_key, generate_secret_key


def split_shared_pair(apps, schema_editor):
    FederatedClub = apps.get_model("federation", "FederatedClub")
    for club in FederatedClub.objects.all():
        club.outbound_key = club.inbound_key
        club.outbound_secret = club.inbound_secret
        if not club.inbound_secret.strip():
            club.inbound_secret = generate_secret_key()
        club.save(update_fields=["inbound_secret", "outbound_key", "outbound_secret"])


class Migration(migrations.Migration):

    dependencies = [
        ("federation", "0007_federatedclub_help_and_unique_key"),
    ]

    operations = [
        migrations.RenameField("federatedclub", "api_key", "inbound_key"),
        migrations.RenameField("federatedclub", "our_key_for_them", "inbound_secret"),
        migrations.AlterField(
            model_name="federatedclub",
            name="inbound_secret",
            field=models.CharField(
                default=generate_secret_key,
                editable=False,
                max_length=128,
                verbose_name="Access secret we issued",
            ),
        ),
        migrations.AlterField(
            model_name="federatedclub",
            name="inbound_key",
            field=models.CharField(
                default=generate_public_key,
                editable=False,
                max_length=64,
                unique=True,
                verbose_name="Access key we issued",
            ),
        ),
        migrations.AddField(
            model_name="federatedclub",
            name="outbound_key",
            field=models.CharField(
                blank=True,
                help_text="Starts with pk_. The partner's administrator creates it on their own site, in the record for our club, and sends it to you. Paste it exactly as received.",
                max_length=64,
                verbose_name="Partner's access key",
            ),
        ),
        migrations.AddField(
            model_name="federatedclub",
            name="outbound_secret",
            field=models.CharField(
                blank=True,
                help_text="Starts with sk_. Sent by the partner together with the key, ideally over a different channel (phone, encrypted message). Until both values are filled in, we cannot read the partner's events.",
                max_length=128,
                verbose_name="Partner's access secret",
            ),
        ),
        migrations.RunPython(split_shared_pair, migrations.RunPython.noop),
    ]
