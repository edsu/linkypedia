from celery.decorators import task

@task
def get_external_links(page):
    # TODO: remove circular dependency on linkypedia.wikipedia somehow
    from linkypedia.wikipedia import extlinks
    logger = get_external_links.get_logger()
    logger.info("fetching extlinks for: %s" % page)
    links = extlinks(page)
    logger.info("got: %s" % links)
    return page
