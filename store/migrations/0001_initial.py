# Generated by Django 2.0 on 2019-02-17 11:46

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('receptmanager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemSaleDaily',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('date', models.DateField(default=None, verbose_name='Огноо')),
                ('amount', models.BigIntegerField(default=0, verbose_name='Тоо ширхэг')),
            ],
            options={
                'verbose_name': 'Өдрийн барааны борлуулалт',
                'verbose_name_plural': 'Өдрийн барааны борлуулалт',
                'ordering': ['-date', '-amount'],
            },
        ),
        migrations.CreateModel(
            name='ItemSaleMonthly',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('year', models.IntegerField(default=2017, verbose_name='Он')),
                ('month', models.IntegerField(default=2, verbose_name='Сар')),
                ('amount', models.BigIntegerField(default=0, verbose_name='Тоо ширхэг')),
            ],
            options={
                'verbose_name': 'Сарын барааны борлуулалт',
                'verbose_name_plural': 'Сарын барааны борлуулалт',
                'ordering': ['-year', '-month', 'amount'],
            },
        ),
        migrations.CreateModel(
            name='ItemSaleWeekly',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('date', models.DateField(default=None, verbose_name='Огноо')),
                ('amount', models.BigIntegerField(default=0, verbose_name='Тоо ширхэг')),
            ],
            options={
                'verbose_name': 'Долоо хоногийн барааны борлуулалт',
                'verbose_name_plural': 'Долоо хоногийн барааны борлуулалт',
                'ordering': ['-date', '-amount'],
            },
        ),
        migrations.CreateModel(
            name='SalesData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('amount', models.IntegerField(default=0, verbose_name='Тоо ширхэг')),
                ('total', models.BigIntegerField(default=0, verbose_name='Нийт дүн')),
                ('status', models.SmallIntegerField(choices=[(0, 'Үүссэн'), (1, 'Зарагдсан'), (2, 'Хүргэгдсэн')], default=0, verbose_name='Худалдан авалтын статус')),
            ],
            options={
                'verbose_name': 'Худалдан авалтын мэдээ',
                'verbose_name_plural': 'Худалдан авалтын мэдээнүүд',
                'ordering': ['-created_date'],
            },
        ),
        migrations.CreateModel(
            name='StoreCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('category_name', models.CharField(default='', max_length=100, verbose_name='Ангилал')),
                ('category_order', models.IntegerField(default=0, verbose_name='Дараалал')),
                ('category_icon', models.ImageField(default=None, upload_to='', verbose_name='Зураг')),
                ('category_url', models.CharField(editable=False, max_length=200, null=True)),
                ('dir_path', models.CharField(blank=True, default='', editable=False, max_length=100)),
                ('upload_dir_path', models.CharField(blank=True, default='', editable=False, max_length=100)),
                ('is_active', models.BooleanField(default=True, verbose_name='Идэвхтэй эсэх')),
            ],
            options={
                'verbose_name': 'Барааны Ангилал',
                'verbose_name_plural': 'Барааны Ангилалууд',
                'ordering': ['category_order'],
            },
        ),
        migrations.CreateModel(
            name='StoreItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('item_name', models.CharField(default='', max_length=200, verbose_name='Барааны нэр')),
                ('item_desc', models.CharField(default='', max_length=600, verbose_name='Барааны тайлбар')),
                ('item_price', models.BigIntegerField(default=0, verbose_name='Барааны үнэ')),
                ('item_icon', models.ImageField(default=None, upload_to='', verbose_name='Зураг')),
                ('item_url', models.CharField(editable=False, max_length=200, null=True)),
                ('dir_path', models.CharField(blank=True, default='', editable=False, max_length=100)),
                ('upload_dir_path', models.CharField(blank=True, default='', editable=False, max_length=100)),
                ('is_active', models.BooleanField(default=True, verbose_name='Идэвхтэй эсэх')),
                ('sold_count', models.BigIntegerField(default=0, verbose_name='Зарагдсан тоо')),
                ('sold_count_daily', models.BigIntegerField(default=0, verbose_name='Зарагдсан тоо Өдрөөр')),
                ('sold_count_weekly', models.BigIntegerField(default=0, verbose_name='Зарагдсан тоо долоо хоногоор')),
                ('sold_count_monthly', models.BigIntegerField(default=0, verbose_name='Зарагдсан тоо сараар')),
                ('required_level', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Зарагдах Level')),
                ('category', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='store.StoreCategory')),
            ],
            options={
                'verbose_name': 'Бараа',
                'verbose_name_plural': 'Бараанууд',
                'ordering': ['item_name'],
            },
        ),
        migrations.AddField(
            model_name='salesdata',
            name='item',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='sales', to='store.StoreItem', verbose_name='Бараа'),
        ),
        migrations.AddField(
            model_name='salesdata',
            name='manager',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='sales', to='receptmanager.ReceptManager', verbose_name='Худалдан авагч'),
        ),
        migrations.AddField(
            model_name='itemsaleweekly',
            name='item',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='weekly_sales', to='store.StoreItem', verbose_name='Бараа'),
        ),
        migrations.AddField(
            model_name='itemsalemonthly',
            name='item',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='monthly_sales', to='store.StoreItem', verbose_name='Бараа'),
        ),
        migrations.AddField(
            model_name='itemsaledaily',
            name='item',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='daily_sales', to='store.StoreItem', verbose_name='Бараа'),
        ),
    ]