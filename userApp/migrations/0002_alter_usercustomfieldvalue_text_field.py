# Generated by Django 4.2.17 on 2024-12-23 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercustomfieldvalue',
            name='text_field',
            field=models.TextField(blank=True, null=True),
        ),
    ]
