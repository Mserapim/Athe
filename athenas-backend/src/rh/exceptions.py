# -*- coding: utf-8 -*-


from contrib.utils import getLogger

log = getLogger(__name__)


class ExceptionBase(Exception):

    def __init__(self, **kwargs):
        message = kwargs.get("mensagem", None)
        exception = kwargs.get("exception", None)
        classe_externa = kwargs.get("classe_externa", None)
        self.message = message
        if not message and exception:
            self.message = exception.args[0]
        elif not message and classe_externa:
            self.message = "Erro em %s!" % classe_externa._meta.verbose_name
        msg = exception if exception else self.message
        try:
            log.info(msg)
        except Exception:
            try:
                log.info(msg)
            except Exception:
                pass

    def __str__(self):
        return self.message


def raise_call(exception_class=Exception, msg="Erro"):
    raise exception_class(msg)
