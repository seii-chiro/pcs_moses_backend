# Generated by Django 5.2 on 2025-04-20 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('election', '0006_candidate_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='title',
            field=models.CharField(blank=True, choices=[('Mr.', 'Mr.'), ('Ms.', 'Ms.'), ('Dr.', 'Dr.'), ('Prof.', 'Prof.')], max_length=10, null=True),
        ),
    ]
