# -*- coding: utf-8 -*-

from contrib.utils import getLogger

log = getLogger(__name__)

"""
DEPRECATED
"""

# ----------------------------------SINAIS-------------------------------------------------------------------
# sicap_data_alteracao = Signal(providing_args=['servidor', 'movimentacao'])


# @receiver(post_save, sender=Servidor)
# @receiver(post_save, sender=ServidorLotacao)
# @receiver(post_save, sender=Documento)
# @receiver(post_save, sender=DocsDadosEspecificos)
# @receiver(sicap_data_alteracao)
# def handle_sicap_data_alteracao(sender, instance, **kwargs):
#     servidor = None
#     movimentacao = None
#     try:
#         if 'movimentacao' in kwargs:
#             movimentacao = kwargs.get('movimentacao')
#         if 'servidor' in kwargs:
#             servidor = kwargs.get('servidor')

#         elif sender == Servidor:
#             servidor = instance.pk
#         elif sender == ServidorLotacao:
#             servidor = instance.servidor.pk
#             try:
#                 movimentacao = instance.servidor.posses.latest('data_posse').pk
#             except Exception, e:
#                 log.exception(e)
#         elif sender == Documento:
#             if instance.pessoafisica_set.get().servidor_set.filter().count() > 0:
#                 servidor = instance.pessoafisica_set.get().servidor_set.filter()[0].pk
#         elif sender == DocsDadosEspecificos:
#             if instance.documento_set.get().pessoafisica_set.get().servidor_set.filter().count() > 0:
#                 servidor = instance.documento_set.get().pessoafisica_set.get().servidor_set.filter()[0].pk
#     except (PessoaFisica.DoesNotExist, Documento.DoesNotExist, Servidor.DoesNotExist) as e:
#         log.exception(e)
#     try:
#         data_alteracao = datetime.now()
#         if servidor:
#             Servidor.objects.filter(pk=servidor).update(data_alteracao=data_alteracao)

#         if movimentacao:
#             MovimentacaoPessoal.objects.filter(pk=movimentacao).update(data_alteracao=data_alteracao)
#     except Exception, e:
#         log.info(u'Data de alteração não atualizada!')
#         log.exception(e)
