# -*- coding: utf-8 -*-
# import twitter # bitlyapi
from threading import Thread

from standard.models import Configuration
from contrib.utils import getLogger

log = getLogger("CMSTRACK %s " % __name__)


# class BitLy(object):

#     def __init__(self):
#         cfg = Configuration.get_or_create('cms')
#         self.api = bitlyapi.BitLy(cfg.get('bitly_user'), cfg.get('bitly_token'))

#     def shorten(self, url):
#         try:
#             r = self.api.shorten(longUrl = url)
#         except:
#             return url
#         else:
#             return r.get('url')


class Twitter(object):

    def __init__(self):
        cfg = Configuration.get_or_create("cms")

        # self.api = twitter.Api(
        #     consumer_key=cfg.get('twitter_app_token'),
        #     consumer_secret=cfg.get('twitter_app_token_secret'),
        #     access_token_key=cfg.get('twitter_user_token'),
        #     access_token_secret=cfg.get('twitter_user_token_secret')
        # )

    def tweet(self, message, _async=False):
        tweet_function = self.api.PostUpdate
        if _async:
            tweet_function = lambda x: Thread(
                target=self.api.PostUpdate, args=[x]
            ).start()

        status_message = "Compartilhado com sucesso."
        try:
            log.info("Tweeting: %s | %s" % (message, len(message)))
            tweet_function(message)
        except Exception as e:
            status_message = "Não foi possível publicar. Ou já foi publicado ou existe instabilidade no serviço do twitter."
            log.error(e)
        else:
            log.info("Twitado")
        return status_message

    def tweet_by_model(self, model, _async=False):
        link = BitLy().shorten(model.get_absolute_url())
        hashtags = " ".join(model.get_hashtags()[0:2])
        message_size = 140 - (len(link) + len(hashtags))
        status = str(model)[:message_size]
        message = "%(status)s %(link)s %(hashtags)s" % locals()
        return self.tweet(message, _async)
