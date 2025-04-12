/**
 *
 **/
Ext._define('edocs.processo.admin.processoAdminRestful', {
    extend: 'core.Restful',

    resource: 'EpadProcessoAdmin',

    getFields: function() {
        if(!this._fields)
            this._fields = edocs.processo.admin.processoAdminRestful.superclass.getFields.call(this).concat([
              {name: 'codigo', type: 'string'},
              {name: 'codigo_processo', type: 'string'},
              {name: 'protocolo_externo', type: 'string'},
              {name: 'movimentado', type: 'string'},
              {name: 'assunto_display', type: 'string'},
              {name: 'custo', type: 'string'},
              {name: 'remetente', type: 'string'},
              {name: 'posicao', type: 'string'},
              {name: 'situacao_display', type: 'string'},
              {name: 'paginas', type: 'int'},
              {name: 'volume', type: 'string'},
              {name: 'passo', type: 'int'},
              {name: 'caixa', type: 'string'},
              {name: 'id', type: 'int'},
              {name: 'protocolado_por', type: 'string'},
              {name: 'tipo_documento_unicode', type: 'string'},
              {name: 'resumo', type: 'string'},
              {name: 'sigiloso', type: 'boolean'},
              {name: 'interessados', type: 'list'},
              {name: 'assunto_processo', type: 'int'},
              {name: 'orgao_geral_origem', type: 'int'},
              {name: 'movimentacao', type: 'int'},
            ]);

        return this._fields;
    }
});

core.RestfulGrid.register(
    'edocs.processo.admin.processoAdminRestful',
    'edocs.processo.admin.processoAdminGrid'
);
