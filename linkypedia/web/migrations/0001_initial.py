# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'WikipediaCategory'
        db.create_table('web_wikipediacategory', (
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
        ))
        db.send_create_signal('web', ['WikipediaCategory'])

        # Adding model 'WikipediaPage'
        db.create_table('web_wikipediapage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')()),
            ('title', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('web', ['WikipediaPage'])

        # Adding M2M table for field categories on 'WikipediaPage'
        db.create_table('web_wikipediapage_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('wikipediapage', models.ForeignKey(orm['web.wikipediapage'], null=False)),
            ('wikipediacategory', models.ForeignKey(orm['web.wikipediacategory'], null=False))
        ))
        db.create_unique('web_wikipediapage_categories', ['wikipediapage_id', 'wikipediacategory_id'])

        # Adding model 'Link'
        db.create_table('web_link', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('wikipedia_page', self.gf('django.db.models.fields.related.ForeignKey')(related_name='links', to=orm['web.WikipediaPage'])),
            ('target', self.gf('django.db.models.fields.TextField')()),
            ('website', self.gf('django.db.models.fields.related.ForeignKey')(related_name='links', to=orm['web.Website'])),
        ))
        db.send_create_signal('web', ['Link'])

        # Adding model 'Website'
        db.create_table('web_website', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.TextField')()),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('favicon_url', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('added_by', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('web', ['Website'])

        # Adding model 'WikipediaUser'
        db.create_table('web_wikipediauser', (
            ('username', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('registration', self.gf('django.db.models.fields.DateTimeField')(max_length=255, null=True)),
            ('gender', self.gf('django.db.models.fields.TextField')(null=True)),
            ('edit_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('emailable', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('web', ['WikipediaUser'])

        # Adding M2M table for field wikipedia_pages on 'WikipediaUser'
        db.create_table('web_wikipediauser_wikipedia_pages', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('wikipediauser', models.ForeignKey(orm['web.wikipediauser'], null=False)),
            ('wikipediapage', models.ForeignKey(orm['web.wikipediapage'], null=False))
        ))
        db.create_unique('web_wikipediauser_wikipedia_pages', ['wikipediauser_id', 'wikipediapage_id'])

        # Adding model 'WikipediaGroup'
        db.create_table('web_wikipediagroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('web', ['WikipediaGroup'])

        # Adding M2M table for field wikipedia_users on 'WikipediaGroup'
        db.create_table('web_wikipediagroup_wikipedia_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('wikipediagroup', models.ForeignKey(orm['web.wikipediagroup'], null=False)),
            ('wikipediauser', models.ForeignKey(orm['web.wikipediauser'], null=False))
        ))
        db.create_unique('web_wikipediagroup_wikipedia_users', ['wikipediagroup_id', 'wikipediauser_id'])

        # Adding model 'Crawl'
        db.create_table('web_crawl', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('started', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('finished', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('website', self.gf('django.db.models.fields.related.ForeignKey')(related_name='crawls', to=orm['web.Website'])),
        ))
        db.send_create_signal('web', ['Crawl'])


    def backwards(self, orm):
        
        # Deleting model 'WikipediaCategory'
        db.delete_table('web_wikipediacategory')

        # Deleting model 'WikipediaPage'
        db.delete_table('web_wikipediapage')

        # Removing M2M table for field categories on 'WikipediaPage'
        db.delete_table('web_wikipediapage_categories')

        # Deleting model 'Link'
        db.delete_table('web_link')

        # Deleting model 'Website'
        db.delete_table('web_website')

        # Deleting model 'WikipediaUser'
        db.delete_table('web_wikipediauser')

        # Removing M2M table for field wikipedia_pages on 'WikipediaUser'
        db.delete_table('web_wikipediauser_wikipedia_pages')

        # Deleting model 'WikipediaGroup'
        db.delete_table('web_wikipediagroup')

        # Removing M2M table for field wikipedia_users on 'WikipediaGroup'
        db.delete_table('web_wikipediagroup_wikipedia_users')

        # Deleting model 'Crawl'
        db.delete_table('web_crawl')


    models = {
        'web.crawl': {
            'Meta': {'ordering': "['-started', '-finished']", 'object_name': 'Crawl'},
            'finished': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'started': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'website': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'crawls'", 'to': "orm['web.Website']"})
        },
        'web.link': {
            'Meta': {'object_name': 'Link'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'target': ('django.db.models.fields.TextField', [], {}),
            'website': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': "orm['web.Website']"}),
            'wikipedia_page': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': "orm['web.WikipediaPage']"})
        },
        'web.website': {
            'Meta': {'object_name': 'Website'},
            'added_by': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'favicon_url': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'url': ('django.db.models.fields.TextField', [], {})
        },
        'web.wikipediacategory': {
            'Meta': {'object_name': 'WikipediaCategory'},
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'})
        },
        'web.wikipediagroup': {
            'Meta': {'object_name': 'WikipediaGroup'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'wikipedia_users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'groups'", 'symmetrical': 'False', 'to': "orm['web.WikipediaUser']"})
        },
        'web.wikipediapage': {
            'Meta': {'object_name': 'WikipediaPage'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'pages'", 'symmetrical': 'False', 'to': "orm['web.WikipediaCategory']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.TextField', [], {}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'web.wikipediauser': {
            'Meta': {'object_name': 'WikipediaUser'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'edit_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'emailable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'gender': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'registration': ('django.db.models.fields.DateTimeField', [], {'max_length': '255', 'null': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'wikipedia_pages': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'users'", 'symmetrical': 'False', 'to': "orm['web.WikipediaPage']"})
        }
    }

    complete_apps = ['web']
