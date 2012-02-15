# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'MatchPort'
        db.create_table(u'match_port', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('port', self.gf('django.db.models.fields.CharField')(unique=True, max_length=24)),
        ))
        db.send_create_signal('flowspec', ['MatchPort'])

        # Adding model 'MatchDscp'
        db.create_table(u'match_dscp', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dscp', self.gf('django.db.models.fields.CharField')(max_length=24)),
        ))
        db.send_create_signal('flowspec', ['MatchDscp'])

        # Adding model 'ThenAction'
        db.create_table(u'then_action', (
            ('action', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('action_value', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('flowspec', ['ThenAction'])

        # Adding unique constraint on 'ThenAction', fields ['action', 'action_value']
        db.create_unique(u'then_action', ['action', 'action_value'])

        # Adding model 'Route'
        db.create_table(u'route', (
            ('packetlength', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='PENDING', max_length=20, null=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('expires', self.gf('django.db.models.fields.DateField')(default=datetime.date(2012, 2, 22))),
            ('protocol', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=128, db_index=True)),
            ('destination', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('comments', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('icmptype', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('fragmenttype', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('applier', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('filed', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('tcpflag', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('response', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('icmpcode', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('flowspec', ['Route'])

        # Adding M2M table for field sourceport on 'Route'
        db.create_table(u'route_sourceport', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('route', models.ForeignKey(orm['flowspec.route'], null=False)),
            ('matchport', models.ForeignKey(orm['flowspec.matchport'], null=False))
        ))
        db.create_unique(u'route_sourceport', ['route_id', 'matchport_id'])

        # Adding M2M table for field then on 'Route'
        db.create_table(u'route_then', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('route', models.ForeignKey(orm['flowspec.route'], null=False)),
            ('thenaction', models.ForeignKey(orm['flowspec.thenaction'], null=False))
        ))
        db.create_unique(u'route_then', ['route_id', 'thenaction_id'])

        # Adding M2M table for field dscp on 'Route'
        db.create_table(u'route_dscp', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('route', models.ForeignKey(orm['flowspec.route'], null=False)),
            ('matchdscp', models.ForeignKey(orm['flowspec.matchdscp'], null=False))
        ))
        db.create_unique(u'route_dscp', ['route_id', 'matchdscp_id'])

        # Adding M2M table for field port on 'Route'
        db.create_table(u'route_port', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('route', models.ForeignKey(orm['flowspec.route'], null=False)),
            ('matchport', models.ForeignKey(orm['flowspec.matchport'], null=False))
        ))
        db.create_unique(u'route_port', ['route_id', 'matchport_id'])

        # Adding M2M table for field destinationport on 'Route'
        db.create_table(u'route_destinationport', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('route', models.ForeignKey(orm['flowspec.route'], null=False)),
            ('matchport', models.ForeignKey(orm['flowspec.matchport'], null=False))
        ))
        db.create_unique(u'route_destinationport', ['route_id', 'matchport_id'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'MatchPort'
        db.delete_table(u'match_port')

        # Deleting model 'MatchDscp'
        db.delete_table(u'match_dscp')

        # Deleting model 'ThenAction'
        db.delete_table(u'then_action')

        # Removing unique constraint on 'ThenAction', fields ['action', 'action_value']
        db.delete_unique(u'then_action', ['action', 'action_value'])

        # Deleting model 'Route'
        db.delete_table(u'route')

        # Removing M2M table for field sourceport on 'Route'
        db.delete_table('route_sourceport')

        # Removing M2M table for field then on 'Route'
        db.delete_table('route_then')

        # Removing M2M table for field dscp on 'Route'
        db.delete_table('route_dscp')

        # Removing M2M table for field port on 'Route'
        db.delete_table('route_port')

        # Removing M2M table for field destinationport on 'Route'
        db.delete_table('route_destinationport')
    
    
    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'flowspec.matchdscp': {
            'Meta': {'object_name': 'MatchDscp', 'db_table': "u'match_dscp'"},
            'dscp': ('django.db.models.fields.CharField', [], {'max_length': '24'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'flowspec.matchport': {
            'Meta': {'object_name': 'MatchPort', 'db_table': "u'match_port'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'port': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '24'})
        },
        'flowspec.route': {
            'Meta': {'object_name': 'Route', 'db_table': "u'route'"},
            'applier': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'destination': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'destinationport': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'matchDestinationPort'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['flowspec.MatchPort']"}),
            'dscp': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['flowspec.MatchDscp']", 'null': 'True', 'blank': 'True'}),
            'expires': ('django.db.models.fields.DateField', [], {'default': 'datetime.date(2012, 2, 22)'}),
            'filed': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'fragmenttype': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'icmpcode': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'icmptype': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '128', 'db_index': 'True'}),
            'packetlength': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'port': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'matchPort'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['flowspec.MatchPort']"}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'response': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'sourceport': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'matchSourcePort'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['flowspec.MatchPort']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'PENDING'", 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'tcpflag': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'then': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['flowspec.ThenAction']", 'symmetrical': 'False'})
        },
        'flowspec.thenaction': {
            'Meta': {'unique_together': "(('action', 'action_value'),)", 'object_name': 'ThenAction', 'db_table': "u'then_action'"},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'action_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['flowspec']
