# Generated by Django 5.1.1 on 2024-10-12 19:28

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0004_rename_total_amount_invoice_amount_paid_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='date_updated',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]