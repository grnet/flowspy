# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Peer.peer_id'
        db.alter_column(u'peer', 'peer_id', self.gf('django.db.models.fields.AutoField')(primary_key=True))

    def backwards(self, orm):

        # Changing field 'Peer.peer_id'
        db.alter_column(u'peer', 'peer_id', self.gf('django.db.models.fields.IntegerField')(primary_key=True))

    models = {
        'peers.peer': {
            'Meta': {'ordering': "['peer_name']", 'object_name': 'Peer', 'db_table': "u'peer'"},
            'domain_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'networks': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['peers.PeerRange']", 'null': 'True', 'blank': 'True'}),
            'peer_as': ('django.db.models.fields.IntegerField', [], {}),
            'peer_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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