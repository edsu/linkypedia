import re
import sys
import logging

import irclib

from linkypedia.web import tasks

RETRIES_BETWEEN_API_ERRORS = 5
IRC_MESSAGE_PATTERN = re.compile('\[\[(.+?)\]\] (.+)? (http:.+?)? (?:\* (.+?) \*)? (?:\(([+-]\d+)\))? (.+)?')

log = logging.getLogger()

class WikipediaUpdatesClient(irclib.SimpleIRCClient):
    """Fetch live update feed from irc://irc.wikimedia.org/en.wikipedia
    """

    def __init__(self, lang):
        super(WikipediaUpdatesClient, self).__init__()
        self.lang = lang

    def on_error(self, connection, event):
        log.error("encountered an irc error: %s" % event)

    def on_created(self, connection, event):
        log.info("joining #%s.wikipedia" % self.lang)
        connection.join("#%s.wikipedia" % self.lang)

    def on_pubmsg(self, connection, event):
        msg = self._strip_color(event.arguments()[0])
        msg = msg.decode("utf-8")
        log.debug(msg)
        match = IRC_MESSAGE_PATTERN.search(msg)
        if match:
            page, status, diff_url, user, bytes_changed, msg = match.groups()

            # ignore what look like non-articles
            if ':' not in page:
                # add the page to the external link celery queue
                result = tasks.get_external_links.delay(lang, page)
                # wait till we get the response
                page_id, created, deleted = result.get()
                log.info("%s (%s) links created=%s, links deleted=%s" % 
                        (page, page_id, created, deleted))
        else:
            # should never happen
            log.fatal("irc message didn't match regex: %s" % msg)
            connection.close()
            sys.exit(-1)


    def _strip_color(self, msg):
        # should remove irc color coding
        return re.sub(r"(\x03|\x02)([0-9]{1,2}(,[0-9]{1,2})?)?", "", msg)


def start_update_stream(username, lang):
    irc = WikipediaUpdatesClient(lang)
    irc.connect("irc.wikimedia.org", 6667, username)
    irc.start()
