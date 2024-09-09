# Generated by Django 5.1 on 2024-09-09 13:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("listings", "0004_listing_event_date_listing_listing_type_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="listing",
            name="condition",
            field=models.CharField(
                blank=True,
                choices=[
                    ("new", "New"),
                    ("like_new", "Like New"),
                    ("good", "Good"),
                    ("fair", "Fair"),
                    ("poor", "Poor"),
                    ("na", "Not Applicable"),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="listing",
            name="price_type",
            field=models.CharField(
                choices=[
                    ("fixed", "Fixed Price"),
                    ("negotiable", "Negotiable"),
                    ("free", "Free"),
                    ("contact", "Contact for Price"),
                    ("na", "Not Applicable"),
                ],
                default="fixed",
                max_length=20,
            ),
        ),
    ]
