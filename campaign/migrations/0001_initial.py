# Generated by Django 2.0 on 2019-02-17 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('product_name', models.CharField(default='', max_length=200, verbose_name='Бүтээгдэхүүний нэр')),
                ('product_desc', models.TextField(verbose_name='Бүтээгдэхүүний тайлбар')),
                ('product_hash', models.CharField(default='', max_length=200, unique=True, verbose_name='Бүтээгдэхүүний #hash')),
                ('is_active', models.BooleanField(default=True, verbose_name='Идэвхтэй эсэх')),
                ('start_date', models.DateTimeField(default=None, verbose_name='Хөтөлбөр эхлэх огноо')),
                ('end_date', models.DateTimeField(default=None, verbose_name='Хөтөлбөр дуусах огноо')),
                ('add_on_comment', models.IntegerField(default=15, verbose_name='Комментод өгөх xp')),
                ('add_on_like', models.IntegerField(default=10, verbose_name='Like-д өгөх xp')),
                ('add_on_test', models.IntegerField(default=10, verbose_name='Тестэнд нэг зөв хариултанд өгөх xp')),
                ('add_on_total_test', models.IntegerField(default=0, verbose_name='Нийт тестэнд өгөх xp')),
                ('add_on_advise', models.IntegerField(default=1, verbose_name='Зөвөлгөөнд өгөх xp')),
                ('add_on_share', models.IntegerField(default=100, verbose_name='Шэйрт өгөх xp')),
                ('campaign_type', models.IntegerField(choices=[(0, 'Энгийн хөтөлбөр'), (1, 'Хугацаат хөтөлбөр')], default=0, verbose_name='Хөтөлбөрийн төрөл')),
                ('add_on_total', models.IntegerField(default=0, verbose_name='Боломжит xp')),
                ('add_on_grand_total', models.IntegerField(default=0, verbose_name='Боломжит нийт xp')),
                ('xp_total', models.IntegerField(default=0, verbose_name='Нийт авсан xp')),
                ('post_count', models.IntegerField(default=0, verbose_name='Нийт материалын тоо')),
                ('advice_count', models.IntegerField(default=0, verbose_name='Нийт зөвөлгөөний тоо')),
                ('campaign_category', models.IntegerField(choices=[(0, 'Эмийн санчид'), (1, 'Гоо сайханчид')], default=None, verbose_name='Хөтөлбөрийн хамаарал')),
                ('coin_start_date', models.DateTimeField(default=None, null=True, verbose_name='Мойл олгож эхлэх огноо')),
                ('coin_end_date', models.DateTimeField(default=None, null=True, verbose_name='Мойл олгож дуусаг огноо')),
            ],
            options={
                'verbose_name': 'Хөтөлбөр',
                'verbose_name_plural': 'Хөтөлбөрүүд',
                'ordering': ['-created_date'],
            },
        ),
        migrations.CreateModel(
            name='CampaignAxis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('axis_product_id', models.IntegerField(blank=True, null=True, verbose_name='Axis Product ID')),
                ('axis_xp_multiply', models.FloatField(blank=True, null=True, verbose_name='XP Multiply')),
            ],
            options={
                'verbose_name': 'Axis-н мэдээлэл',
                'verbose_name_plural': 'Axis-н мэдээлэлүүд',
                'ordering': ['-created_date'],
            },
        ),
        migrations.CreateModel(
            name='CampaignData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('is_test_given', models.BooleanField(default=False, verbose_name='Тест өгсөн эсэх')),
                ('xp_on_comment', models.IntegerField(default=0, verbose_name='Комментоос авсан xp')),
                ('xp_on_like', models.IntegerField(default=0, verbose_name='Like-аас авсан xp')),
                ('xp_on_test', models.IntegerField(default=0, verbose_name='Тестнээс авсан xp')),
                ('xp_on_advise', models.IntegerField(default=0, verbose_name='Зөвөлгөөнөөс авсан xp')),
                ('xp_on_share', models.IntegerField(default=0, verbose_name='Шэйрээс авсан xp')),
                ('xp_total', models.IntegerField(default=0, verbose_name='Нийт авсан xp')),
                ('result_on_test', models.CharField(blank=True, default='', max_length=500, verbose_name='Тест бөглөсөн байдал')),
                ('advise_url', models.URLField(blank=True, default='', null=True, verbose_name='Зөвлөгөөний линк')),
                ('liked_posts', models.TextField(blank=True, default='', null=True, verbose_name='Лайк дарсан постууд')),
                ('commented_posts', models.TextField(blank=True, default='', null=True, verbose_name='Коммент бичсэн постууд')),
                ('shared_posts', models.TextField(blank=True, default='', null=True, verbose_name='Шэйрлэсэн постууд')),
                ('correct_answers_count', models.IntegerField(default=0, verbose_name='Зөв хариултын тоо')),
            ],
            options={
                'verbose_name': 'Дата',
                'verbose_name_plural': 'Дата',
                'ordering': ['-created_date'],
            },
        ),
    ]