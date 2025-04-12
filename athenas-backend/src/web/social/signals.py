# -*- coding: utf-8 -*-
import sys
from web.social.share import Twitter
from threading import Thread
from contrib.utils import getLogger

log = getLogger("CMSTRACK %s " % __name__)


class SocialNetworkModelWrapper:

    def is_published(self):
        raise Exception("Need to implement is_published method in %s" % self)

    def get_hashtags(self):
        raise Exception("Need to implement get_hasgtags method in %s" % self)

    def get_absolute_url(self):
        raise Exception("Need to implement get_permalink method in %s" % self)


def signal_socialnetwork_post_save(sender, instance=None, created=None, **kargs):
    log.info("Executing tweet signal")
    for a in instance.areas.all():
        if a.can_share and hasattr(instance, "post"):
            log.info("Involking tweet thread")
            instance.is_published() and Thread(
                target=Twitter().tweet_by_model, args=[instance.post]
            ).start()
