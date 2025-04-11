/**
 *
 **/
Ext._define('edocs.processo.consulta.processoComumRestful', {
    extend: 'core.Restful',

    resource: 'EpadProcessoComum',

    getFields: function() {
        if(!this._fields)
            this._fields = edocs.processo.consulta.processoComumRestful.superclass.getFields.call(this).concat([
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
              {name: 'caixa', type: 'string'},
              {name: 'id', type: 'int'},
              {name: 'protocolado_por', type: 'string'},
              {name: 'tipo_documento_unicode', type: 'string'},
              {name: 'resumo', type: 'string'},
              {name: 'sigiloso', type: 'boolean'},
              {name: 'interessados', type: 'list'},
            ]);

        return this._fields;
    }
});

core.RestfulGrid.register(
    'edocs.processo.consulta.processoComumRestful',
    'edocs.processo.consulta.processoComumGrid'
);
