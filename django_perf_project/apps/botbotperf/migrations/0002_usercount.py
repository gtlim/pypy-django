# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('botbotperf', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, help_text='', auto_created=True)),
                ('dt', models.DateField(help_text='')),
                ('counts', models.IntegerField(help_text='')),
                ('channel', models.ForeignKey(help_text='', to='botbotperf.Channel')),
            ],
        ),
    ]
