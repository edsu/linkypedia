from celery.decorators import task

from linkypedia.web import models as m
from linkypedia.wikipedia.api import extlinks, info


@task
def get_external_links(page):
    """given page title this task fetches external links from wikipedia
    updates the database, and returns counts of links created and links
    deleted.
    """
    logger = get_external_links.get_logger()
    logger.debug("fetching extlinks for: %s" % page)
    links = extlinks(page)

    article = article_id = None
    created = deleted = 0

    # we only track articles with links
    if links['namespace_id'] == 0 and len(links['urls']) > 0:
        try:
            article = m.Article.objects.get(id=links['page_id'])
        except m.Article.DoesNotExist:
            i = info(page)
            article = m.Article.objects.create(id=i['pageid'], title=page)
            logger.info(u"created article for %s" % page)
        finally:
            if article:
                created, deleted = article.update_links(links['urls'])
                article_id = article.id
                logger.info(u"updated links for %s (%s): created=%s deleted=%s" %
                        (page, article.id, created, deleted))
            else:
                logger.warning(u"hmmm this shouldn't happen for %s?" % page)

    return article_id, created, deleted
