# Generated by Django 3.2.5 on 2021-07-14 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_auto_20210714_2230'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteStatistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateField()),
            ],
        ),
    ]
