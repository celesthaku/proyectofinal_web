# Generated by Django 4.2 on 2024-03-05 20:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_alter_order_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='dni',
            field=models.IntegerField(default='71449234'),
        ),
    ]
