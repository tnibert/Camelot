# Generated by Django 2.0.3 on 2018-07-23 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('camelot', '0011_auto_20180617_0319'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='exiforientation',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]
