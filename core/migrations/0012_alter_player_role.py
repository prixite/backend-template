# Generated by Django 3.2.3 on 2021-06-08 01:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_emailverification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='role',
            field=models.CharField(choices=[('goal-keeper', 'Goalkeeper'), ('defender', 'Defender'), ('mid-fielder', 'Midfielder'), ('attacker', 'Attacker')], max_length=20),
        ),
    ]
