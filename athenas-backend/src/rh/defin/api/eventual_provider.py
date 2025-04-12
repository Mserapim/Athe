from datetime import datetime

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from contrib.decorator import login_required
from django.core.exceptions import ValidationError

from rh.models import (
    PessoaFisica,
    Servidor,
    SocialSecurityEmployee,
    SocialSecurityConfig,
    Localidade,
)

log = getLogger(__name__)


class DEFINEventualProviderPFRestful(RestfulDRY):

    full_text_index = ("social_name__icontains", "cpf__icontains")

    _model = PessoaFisica

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.defin.eventual_provider.pf.Manage")')

    def get_query(self):
        query = super(DEFINEventualProviderPFRestful, self).get_query()
        return query.filter(servidor__type_by_possession="COE")

    def model_to_dict(self, instance):
        params = super(DEFINEventualProviderPFRestful, self).model_to_dict(instance)

        params.update(
            {
                "social_name": (
                    instance.social_name if instance.social_name else instance.nome
                ),
            }
        )
        return params

    def do_post(self):
        """Executa uma requisição POST.

        :returns: Dicionário com mensagem de sucesso ou falha e uma instância.
        """
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        can = self.check_permission(
            self.request.user,
            "add",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )

        if can is False:
            rst.update(
                message="Você não tem permissão para criar %s."
                % self.Model._meta.object_name
            )
        else:
            try:
                params = self.get_params(self.request.POST, check_case=True)
                params.update({"nome": params["social_name"]})
                inst = self.factoryModel(**params)

                cpf = inst.cpf.replace(".", "").replace("-", "")
                if PessoaFisica.objects.filter(cpf=cpf).exists():
                    inst = PessoaFisica.objects.get(cpf=cpf)

                else:
                    inst.grau_instrucao = 18
                    inst.sexo = "N"  # NÃO INFORMADO
                    inst.municipio_naturalidade = Localidade.objects.get(
                        pk=12360
                    )  # NÃO INFORMADO/NA

                    if self.use_full_clean:
                        inst.full_clean()

                    PessoaFisica.validate_coe_employee(inst)

                    inst.save()

                    self.fill_instance_m2m(inst, params)

                servidor = Servidor()
                servidor.pessoa_fisica = inst
                servidor.type_by_possession = "COE"
                servidor.ativo = True
                servidor.save()

                previdencia = SocialSecurityEmployee()
                previdencia.employee = servidor
                previdencia.mass_segregation_plan = 2
                # "RGPS, Plano previdenciário ou único - INSTITUTO NACIONAL DE SEGURIDADE SOCIAL
                rgps = SocialSecurityConfig.objects.get(pk=1)
                previdencia.social_security_config = rgps
                previdencia.start_validity = datetime.today()
                previdencia.save()

            except ValidationError as e:
                log.exception(e)
                rst.update(
                    errors=[
                        {"field": key, "values": value}
                        for key, value in e.message_dict.items()
                    ],
                    message="Alguns campos não foram preenchidos corretamente.",
                )
            except Exception as e:
                try:
                    errors = [
                        {"field": key, "values": value}
                        for key, value in e.message_dict.items()
                    ]
                    rst.update(message=str(errors[0]["values"][0]))
                except:
                    rst.update(message=str(e))
                log.exception(e)
            else:
                rst.update(
                    {
                        "success": True,
                        "message": "Dados persistido com sucesso.",
                        "instance": self.model_to_dict(inst),
                    }
                )

        return rst

    def do_put(self, pk=None):
        """Executa uma requisição PUT.

        :param pk: Chave primária de uma instância. (Opcional)
        :type pk: Integer
        """
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )

        if can is False:
            rst.update(
                message="Você não tem permissão para alterar %s."
                % self.Model._meta.object_name
            )
        else:
            params = self.get_params(self.request.PUT, check_case=True)
            inst = self.factoryModel(**params)
            PessoaFisica.validate_coe_employee(inst)

            rst.update(
                self.do_put_multi()
                if "filter" in self.request.PUT
                else self.do_put_single(pk)
            )

        return rst
