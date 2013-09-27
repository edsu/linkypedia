from django.core.management.base import BaseCommand

from linkypedia. wikipedia import links

class Command(BaseCommand):

    def handle(self, website_url, **kwargs):
        langs = ["ar", "bg", "ca", "cs", "da", "de", "el", "en", "eo", "es",
                "eu", "fa", "fi", "fr", "he", "hu", "id", "it", "ja", "ko",
                "lt", "ms", "nl", "no", "pl", "pt", "ro", "ru", "sk", "sl",
                "sv", "tr", "uk", "vi", "vo", "zh"]
        for lang in langs:
            for src, target in links(website_url, lang=lang):
                print lang, "\t", src.encode('utf8'), "\t", target.encode('utf8')
        

