# Generated by Django 3.2.10 on 2022-03-19 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CollegeAdmin', '0003_busallotmentdata_busrequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bustimings',
            name='time',
            field=models.TimeField(),
        ),
    ]
