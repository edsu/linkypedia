# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'WikipediaPage.views'
        db.alter_column('web_wikipediapage', 'views', self.gf('django.db.models.fields.IntegerField')())


    def backwards(self, orm):
        
        # Changing field 'WikipediaPage.views'
        db.alter_column('web_wikipediapage', 'views', self.gf('django.db.models.fields.IntegerField')(null=True))


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
            'url': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'views': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'views_last': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
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
