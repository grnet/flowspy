# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import flowspec.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FragmentType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fragmenttype', models.CharField(max_length=20, verbose_name=b'Fragment Type', choices=[(b'dont-fragment', b"Don't fragment"), (b'first-fragment', b'First fragment'), (b'is-fragment', b'Is fragment'), (b'last-fragment', b'Last fragment'), (b'not-a-fragment', b'Not a fragment')])),
            ],
        ),
        migrations.CreateModel(
            name='MatchDscp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dscp', models.CharField(max_length=24)),
            ],
            options={
                'db_table': 'match_dscp',
            },
        ),
        migrations.CreateModel(
            name='MatchPort',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('port', models.CharField(unique=True, max_length=24)),
            ],
            options={
                'db_table': 'match_port',
            },
        ),
        migrations.CreateModel(
            name='MatchProtocol',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('protocol', models.CharField(unique=True, max_length=24)),
            ],
            options={
                'db_table': 'match_protocol',
            },
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.SlugField(max_length=128, verbose_name='Name')),
                ('source', models.CharField(help_text='Network address. Use address/CIDR notation', max_length=32, verbose_name='Source Address')),
                ('destination', models.CharField(help_text='Network address. Use address/CIDR notation', max_length=32, verbose_name='Destination Address')),
                ('icmpcode', models.CharField(max_length=32, null=True, verbose_name=b'ICMP Code', blank=True)),
                ('icmptype', models.CharField(max_length=32, null=True, verbose_name=b'ICMP Type', blank=True)),
                ('packetlength', models.IntegerField(null=True, verbose_name=b'Packet Length', blank=True)),
                ('tcpflag', models.CharField(max_length=128, null=True, verbose_name=b'TCP flag', blank=True)),
                ('filed', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(default=b'PENDING', choices=[(b'ACTIVE', b'ACTIVE'), (b'ERROR', b'ERROR'), (b'EXPIRED', b'EXPIRED'), (b'PENDING', b'PENDING'), (b'OUTOFSYNC', b'OUTOFSYNC'), (b'INACTIVE', b'INACTIVE'), (b'ADMININACTIVE', b'ADMININACTIVE')], max_length=20, blank=True, null=True, verbose_name='Status')),
                ('expires', models.DateField(default=flowspec.models.days_offset, verbose_name='Expires')),
                ('response', models.CharField(max_length=512, null=True, verbose_name='Response', blank=True)),
                ('comments', models.TextField(null=True, verbose_name='Comments', blank=True)),
                ('requesters_address', models.CharField(max_length=255, null=True, blank=True)),
                ('applier', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('destinationport', models.ManyToManyField(related_name='matchDestinationPort', verbose_name='Destination Port', to='flowspec.MatchPort', blank=True)),
                ('dscp', models.ManyToManyField(to='flowspec.MatchDscp', verbose_name=b'DSCP', blank=True)),
                ('fragmenttype', models.ManyToManyField(to='flowspec.FragmentType', verbose_name=b'Fragment Type', blank=True)),
                ('port', models.ManyToManyField(related_name='matchPort', verbose_name='Port', to='flowspec.MatchPort', blank=True)),
                ('protocol', models.ManyToManyField(to='flowspec.MatchProtocol', verbose_name='Protocol', blank=True)),
                ('sourceport', models.ManyToManyField(related_name='matchSourcePort', verbose_name='Source Port', to='flowspec.MatchPort', blank=True)),
            ],
            options={
                'db_table': 'route',
                'verbose_name': 'Rule',
                'verbose_name_plural': 'Rules',
            },
        ),
        migrations.CreateModel(
            name='ThenAction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.CharField(max_length=60, verbose_name=b'Action', choices=[(b'accept', b'Accept'), (b'discard', b'Discard'), (b'community', b'Community'), (b'next-term', b'Next term'), (b'routing-instance', b'Routing Instance'), (b'rate-limit', b'Rate limit'), (b'sample', b'Sample')])),
                ('action_value', models.CharField(max_length=255, null=True, verbose_name=b'Action Value', blank=True)),
            ],
            options={
                'ordering': ['action', 'action_value'],
                'db_table': 'then_action',
            },
        ),
        migrations.AlterUniqueTogether(
            name='thenaction',
            unique_together=set([('action', 'action_value')]),
        ),
        migrations.AddField(
            model_name='route',
            name='then',
            field=models.ManyToManyField(to='flowspec.ThenAction', verbose_name='Then'),
        ),
    ]
