# Generated by Django 2.0.7 on 2019-02-17 13:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('receptmanager', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sales',
            name='manager',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='manager_sales', to='receptmanager.ReceptManager', verbose_name='Эмийн санч'),
        ),
    ]