# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Peer',
            fields=[
                ('peer_id', models.AutoField(serialize=False, primary_key=True)),
                ('peer_name', models.CharField(max_length=128)),
                ('peer_as', models.IntegerField(null=True, blank=True)),
                ('peer_tag', models.CharField(max_length=64)),
                ('domain_name', models.CharField(max_length=128, null=True, blank=True)),
            ],
            options={
                'ordering': ['peer_name'],
                'db_table': 'peer',
                'managed': settings.PEER_MANAGED_TABLE,
            },
        ),
        migrations.CreateModel(
            name='PeerRange',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('network', models.CharField(max_length=128)),
            ],
            options={
                'ordering': ['network'],
                'db_table': 'peer_range',
                'managed': settings.PEER_RANGE_MANAGED_TABLE,
            },
        ),
        migrations.CreateModel(
            name='TechcEmail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.CharField(max_length=352, db_column=b'email')),
            ],
            options={
                'db_table': 'techc_email',
                'managed': settings.PEER_TECHC_MANAGED_TABLE,
            },
        ),
        migrations.CreateModel(
            name='PeerNotify',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('peer_activation_notified', models.BooleanField(default=True)),
                ('peer', models.ForeignKey(to='peers.Peer', db_constraint=settings.PEER_MANAGED_TABLE)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'peers_peernotify',
            },
        ),
    ]
