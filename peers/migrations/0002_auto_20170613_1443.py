# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('peers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='peer',
            name='networks',
            field=models.ManyToManyField(to='peers.PeerRange', blank=True),
        ),
        migrations.AddField(
            model_name='peer',
            name='techc_emails',
            field=models.ManyToManyField(to='peers.TechcEmail', blank=True),
        ),
    ]
