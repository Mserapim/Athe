# -*- coding: utf-8 -*-
from rh.gfp.models import ContraCheque
from rh.models import Servidor, MovimentacaoPessoal, SituacaoFuncional, CargaHoraria
from django.db.models import Q
from contrib.middleware import set_current_user


def clear(registers=[]):
    set_current_user("athenas")
    for s in Servidor.objects.filter(Q(type_by_possession="JCA")):
        if s.pessoa_fisica.pensao_pensionista.exists() or s.matricula in registers:
            MovimentacaoPessoal.objects.filter(
                servidor=s, servidor__type_by_possession="JCA"
            ).delete()
            SituacaoFuncional.objects.filter(
                servidor=s, servidor__type_by_possession="JCA"
            ).delete()
            CargaHoraria.objects.filter(
                servidor=s, servidor__type_by_possession="JCA"
            ).delete()
            ContraCheque.objects.filter(
                servidor=s, servidor__type_by_possession="JCA"
            ).delete()
            s.delete()
        else:
            print(s)
