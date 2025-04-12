from asyncio.log import logger
import json
import datetime
import random
from django.utils import timezone
from logging import Handler


class DBHandler(Handler, object):
    model_name = None
    expiry = None

    def __init__(self, model="", expiry=0):
        super(DBHandler, self).__init__()
        self.model_name = model
        self.expiry = int(expiry)

    def emit(self, record):
        try:
            model = self.get_model(self.model_name)
            logger_name = record.funcName
            log_entry = model(
                level=record.levelno,
                msg=record.msg,
                logger_name=logger_name,
                path=record.pathname,
            )
            log_entry.save()

            # in 20% of time, check and delete expired logs
            if self.expiry and random.randint(1, 5) == 1:
                model.objects.filter(
                    create_datetime=timezone.now()
                    - datetime.timedelta(seconds=self.expiry)
                ).delete()
        except Exception as e:
            print(e)

    def get_model(self, name):
        names = name.split(".")
        mod = __import__(".".join(names[:-1]), fromlist=names[-1:])
        return getattr(mod, names[-1])
