# Generated by Django 3.2.10 on 2022-01-02 16:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0004_alter_register_password'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='register',
            name='username',
        ),
    ]
