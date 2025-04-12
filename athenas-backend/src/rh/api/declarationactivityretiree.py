# # -*- coding: utf-8 -*-

# from contrib.newrest import RestfulDRY
# from rh.api.movimentacao import RHMovimentacaoPessoalRestful
# from rh.models import DeclarationActivityRetiree


# class RHDeclarationActivityRetireeRestful(RestfulDRY):

#     _model = DeclarationActivityRetiree

#     full_text_index = (
#         'servidor__matricula__icontains',
#         'servidor__pessoa_fisica__nome__icontains',
#         'servidor__user__username__icontains',
#         'servidor__pessoa_fisica__cpf__icontains',
#         'servidor__pessoa_fisica__rg__icontains',
#         'servidor__matricula_origem__icontains',
#     )

#     exclude_fields = RHMovimentacaoPessoalRestful.exclude_fields + ['movimentacaopessoal_ptr']

#     def json(self, args=[]):
#         self.response['content-type'] = 'text/javascript'
#         self.response.write('Ext._create("rh.declarationactivityretiree.Manage")')
