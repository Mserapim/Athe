# -*- coding: utf-8 -*-
import future


def athenas_future():
    """
    DEPRECATED. This will be removed in migration to python 3.
    """
    import sys
    import traceback
    from contrib.utils import getLogger, show_trace

    if sys.version_info.major == 2:
        # import future
        # from builtins import str
        from builtins import (
            bytes,
            dict,
            int,
            list,
            object,
            range,
            str,
            ascii,
            chr,
            hex,
            input,
            next,
            oct,
            open,
            pow,
            round,
            super,
            filter,
            map,
            zip,
        )

        log = getLogger(__name__)

        log.warn(
            ">>>>>>>  This method %s is DEPRECATED! <<<<<<<" % (athenas_future.__name__)
        )
        # log.warn('>>>>>>>  This method %s is DEPRECATED! %s <<<<<<<' % (athenas_future.__name__, sys.path))
        # show_trace(log.warn, traceback.extract_stack(), indent_size=2,)
