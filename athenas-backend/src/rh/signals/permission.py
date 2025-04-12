# -*- coding: utf-8 -*-

from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from rh.models import Pessoa, PessoaFisica


""" Esse sinal foi criado devido a necessidade que surgiu ao permitir ao usuário gerenciar o cadastro de Pessoa através do
aplicativo de Atendimento ao Cidadão (SACI). Observou-se que as permissões de CRUD dada ao usuário para manipular tal cadastro,
possibilitava alteração de informações relacionadas ao Servidor e a Pessoa Jurídica, que pode estar ligada a uma Unidade Administrativa,
Órgão Previdenciário, entre outros Modelos. Logo, qualquer alteração indiscriminada poderia ocasionar um impacto imensurável ao software.

Em decorrência disso, foram criados os sinais validate_has_perm_general_organ e validate_has_perm_person, que serão acionados quando
houver ação sobre os campos ManyToMany do modelo através da interface. Dessa forma quando o usuário tentar adicionar, remover ou limpar
o campo na Window, será realizado chamada ao método da instância que verificará se tal usuário possui permissão.

"""


@receiver(m2m_changed, sender=Pessoa.dado_bancario.through)
@receiver(m2m_changed, sender=PessoaFisica.social_program.through)
@receiver(m2m_changed, sender=PessoaFisica.serious_diseases.through)
@receiver(m2m_changed, sender=PessoaFisica.necessidades_especiais.through)
@receiver(m2m_changed, sender=PessoaFisica.documento.through)
def validate_has_perm_person(sender, instance, action, **kargs):
    if action in ["pre_remove", "pre_add", "pre_clear"]:
        instance.validate_perm_person()
