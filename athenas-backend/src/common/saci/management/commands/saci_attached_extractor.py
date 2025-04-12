# -*- coding: utf-8 -*-

from common.saci.models import Attachment
from judicial.management.commands import attached_extractor


class Command(attached_extractor.Command):

    _model = Attachment
