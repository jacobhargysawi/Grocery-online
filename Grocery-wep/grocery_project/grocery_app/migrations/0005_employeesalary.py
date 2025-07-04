# Generated by Django 5.0.5 on 2025-06-15 17:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grocery_app', '0004_customeranalytics_inventoryreport_delete_contact'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeSalary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_salary', models.DecimalField(decimal_places=2, max_digits=10)),
                ('bonus', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('total_salary', models.DecimalField(decimal_places=2, editable=False, max_digits=10)),
                ('payment_month', models.CharField(max_length=20)),
                ('paid_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(limit_choices_to={'role__in': ['Admin', 'Seller']}, on_delete=django.db.models.deletion.CASCADE, to='grocery_app.user')),
            ],
        ),
    ]
