"""
Initial migration for members app.

Creates the ClubUser model WITHOUT cross-app ForeignKey fields
(photo -> wagtailimages, products -> website) to break circular
migration dependencies. Those are added in 0002.
"""

import django.contrib.auth.models
import django.contrib.auth.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="ClubUser",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False, verbose_name="superuser status")),
                ("username", models.CharField(
                    error_messages={"unique": "A user with that username already exists."},
                    max_length=150, unique=True,
                    validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                    verbose_name="username",
                )),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="email address")),
                ("is_staff", models.BooleanField(default=False, verbose_name="staff status")),
                ("is_active", models.BooleanField(default=True, verbose_name="active")),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined")),
                # --- Custom fields (no cross-app FKs) ---
                ("display_name", models.CharField(blank=True, max_length=100)),
                ("show_real_name_to_members", models.BooleanField(default=False)),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("mobile", models.CharField(blank=True, max_length=30)),
                ("birth_date", models.DateField(blank=True, null=True)),
                ("birth_place", models.CharField(blank=True, max_length=100)),
                ("fiscal_code", models.CharField(blank=True, max_length=16)),
                ("document_type", models.CharField(blank=True, choices=[("id_card", "ID Card"), ("license", "Driver's License"), ("passport", "Passport")], max_length=20)),
                ("document_number", models.CharField(blank=True, max_length=50)),
                ("document_expiry", models.DateField(blank=True, null=True)),
                ("address", models.CharField(blank=True, max_length=255)),
                ("city", models.CharField(blank=True, max_length=100)),
                ("province", models.CharField(blank=True, max_length=2)),
                ("postal_code", models.CharField(blank=True, max_length=5)),
                ("country", models.CharField(default="IT", max_length=2)),
                ("card_number", models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ("membership_date", models.DateField(blank=True, null=True)),
                ("membership_expiry", models.DateField(blank=True, null=True)),
                ("newsletter", models.BooleanField(default=False)),
                ("show_in_directory", models.BooleanField(default=False)),
                ("public_profile", models.BooleanField(default=False)),
                ("bio", models.TextField(blank=True)),
                ("aid_available", models.BooleanField(default=False)),
                ("aid_radius_km", models.PositiveIntegerField(default=25)),
                ("aid_location_city", models.CharField(blank=True, max_length=100)),
                ("aid_coordinates", models.CharField(blank=True, max_length=50)),
                ("aid_notes", models.TextField(blank=True)),
                ("email_notifications", models.BooleanField(default=True)),
                ("push_notifications", models.BooleanField(default=False)),
                ("news_updates", models.BooleanField(default=True)),
                ("event_updates", models.BooleanField(default=True)),
                ("event_reminders", models.BooleanField(default=True)),
                ("membership_alerts", models.BooleanField(default=True)),
                ("partner_updates", models.BooleanField(default=False)),
                ("aid_requests", models.BooleanField(default=True)),
                ("partner_events", models.BooleanField(default=True)),
                ("partner_event_comments", models.BooleanField(default=True)),
                ("digest_frequency", models.CharField(choices=[("immediate", "Immediate"), ("daily", "Daily"), ("weekly", "Weekly")], default="daily", max_length=10)),
                ("groups", models.ManyToManyField(blank=True, related_name="user_set", related_query_name="user", to="auth.group", verbose_name="groups")),
            ],
            options={
                "verbose_name": "club user",
                "verbose_name_plural": "club users",
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
