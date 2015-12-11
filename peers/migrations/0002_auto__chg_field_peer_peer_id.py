# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.conf import settings


# Probably due to a MySQL bug, the AutoField is not created properly and raises a 
# "Warning 1364: Field 'peer_id' doesn't have a default value" exception on inserts via Django admin.
# This does not make sense... No exception comes up once insterts are done via MySQL cli or phpmyadmin
# What seems to cause this issue is a South generated sql query: 
# ALTER TABLE `peer` ALTER COLUMN `peer_id` DROP DEFAULT;
# will have to override _alter_set_defaults
def new_alter_columns_set_default(field, name, params, sqls):
    return

db._alter_set_defaults = new_alter_columns_set_default

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Peer.peer_id'
        if settings.PEER_MANAGED_TABLE:
            db.alter_column(u'peer', 'peer_id', self.gf('django.db.models.fields.AutoField')(primary_key=True))

    def backwards(self, orm):

        # Changing field 'Peer.peer_id'
        if settings.PEER_MANAGED_TABLE:
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