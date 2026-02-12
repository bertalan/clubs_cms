"""
Add cross-app ForeignKey fields that were deferred from 0001 to
break the circular dependency with wagtailimages.
"""

import django.db.models.deletion
from django.db import migrations, models
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("wagtailimages", "0001_initial"),
        ("website", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="clubuser",
            name="photo",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
        migrations.AddField(
            model_name="clubuser",
            name="products",
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True,
                related_name="members",
                to="website.product",
            ),
        ),
        migrations.AddField(
            model_name="clubuser",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                related_name="user_set",
                related_query_name="user",
                to="auth.permission",
                verbose_name="user permissions",
            ),
        ),
    ]
