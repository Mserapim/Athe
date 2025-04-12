# -*- coding: utf-8 -*-

from contrib.newrest import Restful
from contrib.nil import nil_date, nil_datetime, nil_new_display, nil_pk, nil_new_unicode

# from rh.models import *
from contrib.utils import DateUtils, getLogger
from rh.cif.models import AddressCif

log = getLogger(__name__)


class CifAddressCif(Restful):

    _model = AddressCif

    full_text_index = ("municipio__nome__icontains",)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("cif.address.Manage")')

    def has_perm_admin(self):
        current_user = self.request.user.servidor
        return True if current_user.user.has_perm("cif.cif_admin") else False

    def confirm_action(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            address = self._model.objects.filter(
                pk__in=self.request.POST.getlist("pks")
            )
            for addr in address:
                addr.status = 2
                addr.save()
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))
        else:
            rst.update(success=True, message="Dados persistidos com sucesso!")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def block_unblock_action(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            log.info(self.request.POST)
            if self.has_perm_admin():
                address = self._model.objects.filter(
                    pk__in=self.request.POST.getlist("pks")
                )
                for addr in address:
                    addr.block_change = (
                        True if int(self.request.POST.get("action")) == 1 else False
                    )
                    addr.save()
            else:
                raise Exception("Você não possui permissão para realizar essa ação!")
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))
        else:
            rst.update(success=True, message="Dados persistidos com sucesso!")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)
        if "authorization_reside_outside" in params:
            params.update(
                authorization_reside_outside=params.get(
                    "authorization_reside_outside", "off"
                ).lower()
                == "on"
            )

        if "member" in params:
            if params.get("member") != "":
                field = getattr(self.Model, "member")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(member=query.get(pk=params.get("member")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                log.info(">>>|| else do member")
                # cif = ControlInformationMember.objects.get(employee__servidor=self.request.user.servidor, status=1)
                # params.update(member=cif)

        if "refperiod_address" in params:
            if params.get("refperiod_address") != "":
                field = getattr(self.Model, "refperiod_address")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        refperiod_address=query.get(pk=params.get("refperiod_address"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                raise Exception("Preencha o campo Período de Referência!")
                # params.update(refperiod_address=None)

        if "ref_address" in params:
            if params.get("ref_address") != "":
                field = getattr(self.Model, "ref_address")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(ref_address=query.get(pk=params.get("ref_address")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                raise Exception("Preencha o campo Endereço!")
                # params.update(ref_address=None)

        if "start_date" in params:
            if params.get("start_date") != "":
                params.update(
                    start_date=DateUtils.str_to_date(params.get("start_date"))
                )
            else:
                raise Exception("Preencha o campo Data Início Residência!")

        if "end_date" in params:
            if params.get("end_date") != "":
                params.update(end_date=DateUtils.str_to_date(params.get("end_date")))
            else:
                params.update(end_date=None)

        # if 'municipio' in params:
        #     if params.get('municipio') != '':
        #         field = getattr(self.Model, 'municipio')

        #         # mater compatibilidade com django-1.4.x
        #         get_queryset = field.get_queryset
        #         query = get_queryset()

        #         try:
        #             params.update(
        #                 municipio=query.get(pk=params.get('municipio'))
        #             )
        #         except Exception as e:
        #             log.exception(e)
        #             raise e
        #     else:
        #         raise Exception('Preencha o campo Município!')

        # if 'tipo_logradouro' in params:
        #     if params.get('tipo_logradouro') != '':
        #         params.update(tipo_logradouro=params.get('tipo_logradouro'))
        #     else:
        #         raise Exception('Preencha o campo Tipo de Logradouro!')

        # if 'logradouro' in params:
        #     if params.get('logradouro') != '':
        #         params.update(logradouro=params.get('logradouro'))
        #     else:
        #         raise Exception('Preencha o campo Logradouro!')

        # if 'numero' in params:
        #     if params.get('numero') != '':
        #         params.update(numero=params.get('numero'))
        #     else:
        #         raise Exception('Preencha o campo Número!')

        # if 'bairro' in params:
        #     if params.get('bairro') != '':
        #         params.update(bairro=params.get('bairro'))
        #     else:
        #         raise Exception('Preencha o campo Bairro!')

        # if 'cep' in params:
        #     if params.get('cep') != '':
        #         params.update(cep=params.get('cep'))
        #     else:
        #         raise Exception('Preencha o campo CEP!')

        if "type_residence" in params:
            if params.get("type_residence") != "":
                params.update(type_residence=params.get("type_residence"))
            else:
                raise Exception("Preencha o campo Tipo de Residência!")

        # if 'tipo_endereco' in params:
        #     if params.get('tipo_endereco') != '':
        #         params.update(tipo_endereco=params.get('tipo_endereco'))
        #     else:
        #         raise Exception('Preencha o campo Tipo de Endereço!')

        if "previus_addres" in params:
            if params.get("previus_addres") != "":
                field = getattr(self.Model, "previus_addres")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        previus_addres=query.get(pk=params.get("previus_addres"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(previus_addres=None)

        if "file_document" in params:
            if params.get("file_document") != "":
                field = getattr(self.Model, "file_document")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        file_document=query.get(pk=params.get("file_document"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(file_document=None)

        params.update(status=2)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)
        ref_address_unicode = ""
        if instance.ref_address:
            ref_address_unicode = "%s - %s" % (
                instance.ref_address,
                (
                    instance.ref_address.complemento
                    if instance.ref_address.complemento
                    else ""
                ),
            )
        rst.update(
            icons=instance.icons,
            status=instance.status,
            status_display=nil_new_display(instance, "status", ""),
            status_pendency=instance.status_pendency,
            status_pendency_display=nil_new_display(instance, "status_pendency", ""),
            # tipo_logradouro=instance.tipo_logradouro,
            # tipo_logradouro_display=nil_new_display(instance, 'tipo_logradouro', ''),
            # bairro=instance.bairro,
            # data_alteracao=nil_date(instance.data_alteracao, None),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=str(instance.modified_by) or None,
            end_date=nil_date(instance.end_date, None),
            previus_addres=nil_pk(instance.previus_addres, None),
            previus_addres_unicode=nil_new_unicode(instance.previus_addres, ""),
            modified_at=nil_datetime(instance.modified_at, None),
            created_at=nil_datetime(instance.created_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=str(instance.created_by) or None,
            # logradouro=instance.logradouro,
            # numero=instance.numero,
            type_residence=nil_new_unicode(instance.type_residence, ""),
            type_residence_display=nil_new_display(instance, "type_residence", ""),
            member=nil_pk(instance.member, None),
            member_unicode=nil_new_unicode(instance.member, ""),
            # tipo_endereco=instance.tipo_endereco,
            # tipo_endereco_display=nil_new_display(instance, 'tipo_endereco', ''),
            file_document=nil_pk(instance.file_document, None),
            file_document_unicode=nil_new_unicode(instance.file_document, ""),
            # cep=instance.cep,
            # complemento=instance.complemento,
            start_date=nil_date(instance.start_date, None),
            # municipio=nil_pk(instance.municipio, None),
            refperiod_address=nil_pk(instance.refperiod_address, None),
            refperiod_address_unicode=nil_new_unicode(instance.refperiod_address, ""),
            block_change=nil_new_unicode(instance.block_change, ""),
            authorization_reside_outside=nil_new_unicode(
                instance.authorization_reside_outside, ""
            ),
            authorization_status=instance.get_status_outside(),
            ref_address=nil_pk(instance.ref_address, None),
            ref_address_unicode=ref_address_unicode,
        )

        return rst
