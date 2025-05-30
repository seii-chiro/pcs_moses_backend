# Generated by Django 5.2 on 2025-04-21 17:15

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_customuser_image_base64'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voted_at', models.DateTimeField(blank=True, null=True)),
                ('voter_id', models.IntegerField(default=0)),
                ('proxy_for_voter_id', models.IntegerField(default=0)),
                ('candidate_id', models.IntegerField(default=0)),
                ('notes', models.TextField(blank=True, default='')),
                ('is_counted', models.BooleanField(default=False)),
                ('counted_at', models.DateTimeField(blank=True, null=True)),
                ('created_by', models.CharField(blank=True, max_length=50, null=True)),
                ('updated_by', models.CharField(blank=True, max_length=50, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('record_status_id', models.IntegerField(default=1)),
            ],
            options={
                'db_table': 'votes',
            },
        ),
        migrations.AddField(
            model_name='customuser',
            name='finished_voting',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='started_voting',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
