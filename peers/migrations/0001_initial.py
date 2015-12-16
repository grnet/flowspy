# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.conf import settings


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PeerRange'
        if settings.PEER_RANGE_MANAGED_TABLE:
            db.create_table(u'peer_range', (
                ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('network', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ))
            db.send_create_signal('peers', ['PeerRange'])

        # Adding model 'TechcEmail'
        if settings.PEER_TECHC_MANAGED_TABLE:
            db.create_table('techc_email', (
                ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('email', self.gf('django.db.models.fields.CharField')(max_length=352, db_column='email')),
            ))
            db.send_create_signal('peers', ['TechcEmail'])

        # Adding model 'Peer'
        if settings.PEER_MANAGED_TABLE:
            db.create_table(u'peer', (
                ('peer_id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
                ('peer_name', self.gf('django.db.models.fields.CharField')(max_length=128)),
                ('peer_as', self.gf('django.db.models.fields.IntegerField')()),
                ('peer_tag', self.gf('django.db.models.fields.CharField')(max_length=64)),
                ('domain_name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ))
            db.send_create_signal('peers', ['Peer'])

        # Adding M2M table for field networks on 'Peer'
        if settings.PEER_MANAGED_TABLE and settings.PEER_RANGE_MANAGED_TABLE:
            db.create_table(u'peer_networks', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('peer', models.ForeignKey(orm['peers.peer'], null=False)),
                ('peerrange', models.ForeignKey(orm['peers.peerrange'], null=False))
            ))
            db.create_unique(u'peer_networks', ['peer_id', 'peerrange_id'])

        # Adding M2M table for field techc_emails on 'Peer'
        if settings.PEER_MANAGED_TABLE and settings.PEER_TECHC_MANAGED_TABLE:
            db.create_table(u'peer_techc_emails', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('peer', models.ForeignKey(orm['peers.peer'], null=False)),
                ('techcemail', models.ForeignKey(orm['peers.techcemail'], null=False))
            ))
            db.create_unique(u'peer_techc_emails', ['peer_id', 'techcemail_id'])

    def backwards(self, orm):
        # Deleting model 'PeerRange'
        if settings.PEER_RANGE_MANAGED_TABLE:
            db.delete_table(u'peer_range')

        # Deleting model 'TechcEmail'
        if settings.PEER_TECHC_MANAGED_TABLE:
            db.delete_table('techc_email')

        # Deleting model 'Peer'
        if settings.PEER_MANAGED_TABLE:
            db.delete_table(u'peer')

        # Removing M2M table for field networks on 'Peer'
        if settings.PEER_MANAGED_TABLE and settings.PEER_RANGE_MANAGED_TABLE:
            db.delete_table('peer_networks')

        # Removing M2M table for field techc_emails on 'Peer'
        if settings.PEER_MANAGED_TABLE and settings.PEER_TECHC_MANAGED_TABLE:
            db.delete_table('peer_techc_emails')

    models = {
        'peers.peer': {
            'Meta': {'ordering': "['peer_name']", 'object_name': 'Peer', 'db_table': "u'peer'"},
            'domain_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'networks': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['peers.PeerRange']", 'null': 'True', 'blank': 'True'}),
            'peer_as': ('django.db.models.fields.IntegerField', [], {}),
            'peer_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'peer_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'peer_tag': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'techc_emails': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['peers.TechcEmail']", 'null': 'True', 'blank': 'True'})
        },
        'peers.peerrange': {
            'Meta': {'ordering': "['network']", 'object_name': 'PeerRange', 'db_table': "u'peer_range'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'peers.techcemail': {
            'Meta': {'object_name': 'TechcEmail', 'db_table': "'techc_email'"},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '352', 'db_column': "'email'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['peers']
