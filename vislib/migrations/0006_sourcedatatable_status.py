# Generated by Django 3.0.4 on 2020-04-15 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vislib', '0005_auto_20200415_0934'),
    ]

    operations = [
        migrations.AddField(
            model_name='sourcedatatable',
            name='status',
            field=models.IntegerField(default=1),
        ),
    ]