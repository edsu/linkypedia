import logging

from django.core.management.base import BaseCommand

from linkypedia.wikipedia.irc import start_update_stream

logging.basicConfig(
        filename="updates.log", 
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s")

log = logging.getLogger()


class Command(BaseCommand):

    def handle(self, **options):
        log.info("starting irc update daemon")
        start_update_stream("linkypedia")

