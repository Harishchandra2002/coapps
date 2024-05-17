# Generated by Django 5.0.4 on 2024-05-12 03:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee_Data',
            fields=[
                ('emp_id', models.AutoField(primary_key=True, serialize=False)),
                ('employee_name', models.CharField(max_length=100)),
                ('employee_email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=100)),
                ('leave_balance', models.IntegerField(default=10)),
            ],
            options={
                'db_table': 'employees_data',
            },
        ),
    ]
