# Generated by Django 2.0 on 2019-02-19 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receptmanager', '0002_saleslog'),
    ]

    operations = [
        migrations.AddField(
            model_name='sales',
            name='quantity',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=65, verbose_name='Борлуулалтын тоо ширхэг'),
        ),
    ]
