# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'MatchAddress'
        db.create_table(u'match_address', (
            ('destination', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('flowspec', ['MatchAddress'])

        # Adding model 'MatchPort'
        db.create_table(u'match_port', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('port', self.gf('django.db.models.fields.CharField')(max_length=24)),
        ))
        db.send_create_signal('flowspec', ['MatchPort'])

        # Adding model 'MatchDscp'
        db.create_table(u'match_dscp', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dscp', self.gf('django.db.models.fields.CharField')(max_length=24)),
        ))
        db.send_create_signal('flowspec', ['MatchDscp'])

        # Adding model 'MatchFragmentType'
        db.create_table(u'match_fragment_type', (
            ('fragmenttype', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('flowspec', ['MatchFragmentType'])

        # Adding model 'MatchIcmpCode'
        db.create_table(u'match_icmp_code', (
            ('icmp_code', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('flowspec', ['MatchIcmpCode'])

        # Adding model 'MatchIcmpType'
        db.create_table(u'match_icmp_type', (
            ('icmp_type', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('flowspec', ['MatchIcmpType'])

        # Adding model 'MatchPacketLength'
        db.create_table(u'match_packet_length', (
            ('packet_length', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('flowspec', ['MatchPacketLength'])

        # Adding model 'MatchProtocol'
        db.create_table(u'match_protocol', (
            ('protocol', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('flowspec', ['MatchProtocol'])

        # Adding model 'MatchTcpFlag'
        db.create_table(u'match_tcp_flag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tcp_flag', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('flowspec', ['MatchTcpFlag'])

        # Adding model 'ThenAction'
        db.create_table(u'then_action', (
            ('action', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('action_value', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('flowspec', ['ThenAction'])

        # Adding model 'ThenStatement'
        db.create_table(u'then', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('flowspec', ['ThenStatement'])

        # Adding M2M table for field thenaction on 'ThenStatement'
        db.create_table(u'then_thenaction', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('thenstatement', models.ForeignKey(orm['flowspec.thenstatement'], null=False)),
            ('thenaction', models.ForeignKey(orm['flowspec.thenaction'], null=False))
        ))
        db.create_unique(u'then_thenaction', ['thenstatement_id', 'thenaction_id'])

        # Adding model 'MatchStatement'
        db.create_table(u'match', (
            ('matchfragmenttype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['flowspec.MatchFragmentType'], null=True, blank=True)),
            ('matchprotocol', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['flowspec.MatchProtocol'], null=True, blank=True)),
            ('matchicmptype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['flowspec.MatchIcmpType'], null=True, blank=True)),
            ('matchSourcePort', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='matchSourcePort', null=True, to=orm['flowspec.MatchPort'])),
            ('matchicmpcode', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['flowspec.MatchIcmpCode'], null=True, blank=True)),
            ('matchTcpFlag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['flowspec.MatchTcpFlag'], null=True, blank=True)),
            ('matchDestination', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='matchDestination', null=True, to=orm['flowspec.MatchAddress'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('matchpacketlength', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['flowspec.MatchPacketLength'], null=True, blank=True)),
        ))
        db.send_create_signal('flowspec', ['MatchStatement'])

        # Adding M2M table for field matchDestinationPort on 'MatchStatement'
        db.create_table(u'match_matchDestinationPort', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('matchstatement', models.ForeignKey(orm['flowspec.matchstatement'], null=False)),
            ('matchport', models.ForeignKey(orm['flowspec.matchport'], null=False))
        ))
        db.create_unique(u'match_matchDestinationPort', ['matchstatement_id', 'matchport_id'])

        # Adding M2M table for field matchSource on 'MatchStatement'
        db.create_table(u'match_matchSource', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('matchstatement', models.ForeignKey(orm['flowspec.matchstatement'], null=False)),
            ('matchaddress', models.ForeignKey(orm['flowspec.matchaddress'], null=False))
        ))
        db.create_unique(u'match_matchSource', ['matchstatement_id', 'matchaddress_id'])

        # Adding M2M table for field matchdscp on 'MatchStatement'
        db.create_table(u'match_matchdscp', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('matchstatement', models.ForeignKey(orm['flowspec.matchstatement'], null=False)),
            ('matchdscp', models.ForeignKey(orm['flowspec.matchdscp'], null=False))
        ))
        db.create_unique(u'match_matchdscp', ['matchstatement_id', 'matchdscp_id'])

        # Adding M2M table for field matchport on 'MatchStatement'
        db.create_table(u'match_matchport', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('matchstatement', models.ForeignKey(orm['flowspec.matchstatement'], null=False)),
            ('matchport', models.ForeignKey(orm['flowspec.matchport'], null=False))
        ))
        db.create_unique(u'match_matchport', ['matchstatement_id', 'matchport_id'])

        # Adding model 'Route'
        db.create_table(u'route', (
            ('then', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['flowspec.ThenStatement'])),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('expires', self.gf('django.db.models.fields.DateTimeField')()),
            ('applier', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('filed', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('match', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['flowspec.MatchStatement'])),
        ))
        db.send_create_signal('flowspec', ['Route'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'MatchAddress'
        db.delete_table(u'match_address')

        # Deleting model 'MatchPort'
        db.delete_table(u'match_port')

        # Deleting model 'MatchDscp'
        db.delete_table(u'match_dscp')

        # Deleting model 'MatchFragmentType'
        db.delete_table(u'match_fragment_type')

        # Deleting model 'MatchIcmpCode'
        db.delete_table(u'match_icmp_code')

        # Deleting model 'MatchIcmpType'
        db.delete_table(u'match_icmp_type')

        # Deleting model 'MatchPacketLength'
        db.delete_table(u'match_packet_length')

        # Deleting model 'MatchProtocol'
        db.delete_table(u'match_protocol')

        # Deleting model 'MatchTcpFlag'
        db.delete_table(u'match_tcp_flag')

        # Deleting model 'ThenAction'
        db.delete_table(u'then_action')

        # Deleting model 'ThenStatement'
        db.delete_table(u'then')

        # Removing M2M table for field thenaction on 'ThenStatement'
        db.delete_table('then_thenaction')

        # Deleting model 'MatchStatement'
        db.delete_table(u'match')

        # Removing M2M table for field matchDestinationPort on 'MatchStatement'
        db.delete_table('match_matchDestinationPort')

        # Removing M2M table for field matchSource on 'MatchStatement'
        db.delete_table('match_matchSource')

        # Removing M2M table for field matchdscp on 'MatchStatement'
        db.delete_table('match_matchdscp')

        # Removing M2M table for field matchport on 'MatchStatement'
        db.delete_table('match_matchport')

        # Deleting model 'Route'
        db.delete_table(u'route')
    
    
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
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'flowspec.matchaddress': {
            'Meta': {'object_name': 'MatchAddress', 'db_table': "u'match_address'"},
            'destination': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'flowspec.matchdscp': {
            'Meta': {'object_name': 'MatchDscp', 'db_table': "u'match_dscp'"},
            'dscp': ('django.db.models.fields.CharField', [], {'max_length': '24'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'flowspec.matchfragmenttype': {
            'Meta': {'object_name': 'MatchFragmentType', 'db_table': "u'match_fragment_type'"},
            'fragmenttype': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'flowspec.matchicmpcode': {
            'Meta': {'object_name': 'MatchIcmpCode', 'db_table': "u'match_icmp_code'"},
            'icmp_code': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'flowspec.matchicmptype': {
            'Meta': {'object_name': 'MatchIcmpType', 'db_table': "u'match_icmp_type'"},
            'icmp_type': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'flowspec.matchpacketlength': {
            'Meta': {'object_name': 'MatchPacketLength', 'db_table': "u'match_packet_length'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'packet_length': ('django.db.models.fields.IntegerField', [], {})
        },
        'flowspec.matchport': {
            'Meta': {'object_name': 'MatchPort', 'db_table': "u'match_port'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'port': ('django.db.models.fields.CharField', [], {'max_length': '24'})
        },
        'flowspec.matchprotocol': {
            'Meta': {'object_name': 'MatchProtocol', 'db_table': "u'match_protocol'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'flowspec.matchstatement': {
            'Meta': {'object_name': 'MatchStatement', 'db_table': "u'match'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'matchDestination': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'matchDestination'", 'null': 'True', 'to': "orm['flowspec.MatchAddress']"}),
            'matchDestinationPort': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'matchDestinationPort'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['flowspec.MatchPort']"}),
            'matchSource': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'matchSource'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['flowspec.MatchAddress']"}),
            'matchSourcePort': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'matchSourcePort'", 'null': 'True', 'to': "orm['flowspec.MatchPort']"}),
            'matchTcpFlag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['flowspec.MatchTcpFlag']", 'null': 'True', 'blank': 'True'}),
            'matchdscp': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['flowspec.MatchDscp']", 'null': 'True', 'blank': 'True'}),
            'matchfragmenttype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['flowspec.MatchFragmentType']", 'null': 'True', 'blank': 'True'}),
            'matchicmpcode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['flowspec.MatchIcmpCode']", 'null': 'True', 'blank': 'True'}),
            'matchicmptype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['flowspec.MatchIcmpType']", 'null': 'True', 'blank': 'True'}),
            'matchpacketlength': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['flowspec.MatchPacketLength']", 'null': 'True', 'blank': 'True'}),
            'matchport': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['flowspec.MatchPort']", 'null': 'True', 'blank': 'True'}),
            'matchprotocol': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['flowspec.MatchProtocol']", 'null': 'True', 'blank': 'True'})
        },
        'flowspec.matchtcpflag': {
            'Meta': {'object_name': 'MatchTcpFlag', 'db_table': "u'match_tcp_flag'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tcp_flag': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'flowspec.route': {
            'Meta': {'object_name': 'Route', 'db_table': "u'route'"},
            'applier': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'expires': ('django.db.models.fields.DateTimeField', [], {}),
            'filed': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'match': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['flowspec.MatchStatement']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'then': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['flowspec.ThenStatement']"})
        },
        'flowspec.thenaction': {
            'Meta': {'object_name': 'ThenAction', 'db_table': "u'then_action'"},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'action_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'flowspec.thenstatement': {
            'Meta': {'object_name': 'ThenStatement', 'db_table': "u'then'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thenaction': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['flowspec.ThenAction']", 'null': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['flowspec']
