# Generated by Django 5.0.6 on 2024-06-07 17:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('train_routes', '0012_alter_train_image'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='ticket',
            unique_together={('journey', 'seat', 'cargo')},
        ),
    ]
