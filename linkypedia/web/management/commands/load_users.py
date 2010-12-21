import logging

from django.core.management.base import BaseCommand

from linkypedia.wikipedia import crawl

logging.basicConfig(
        filename="load_users.log", 
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s")

class Command(BaseCommand):

    def handle(self, **options):
        created, updated = crawl.load_users()
        logging.info("created %s users and updated %s" % (created, updated))
