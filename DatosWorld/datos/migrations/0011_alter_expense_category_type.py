# Generated by Django 5.1.1 on 2024-10-15 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0010_expense_date_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='category_type',
            field=models.CharField(blank=True, choices=[('Bank Charge', 'Bank Charge'), ('Current Liabilities', 'Current Liabilities'), ('Long-Term Liabilities', 'Long-Term Liabilities'), ('Cost of Goods Sold', 'Cost of Goods Sold'), ('Operating Expenses', 'Operating Expenses'), ('Administrative Expenses', 'Administrative Expenses'), ('Marketing Expenses', 'Marketing Expenses'), ('Depreciation', 'Depreciation'), ('Miscellaneous Expenses', 'Miscellaneous Expenses')], max_length=100, null=True),
        ),
    ]
