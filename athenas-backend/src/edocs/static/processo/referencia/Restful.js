/**
 *
 **/
Ext._define('edocs.processo.referencia.Restful', {
    extend: 'core.Restful',

    resource: 'EpadReferencia',

    getFields: function() {
        if(!this._fields)
            this._fields = edocs.processo.referencia.Restful.superclass.getFields.call(this).concat([
              {name: 'codigo', type: 'string'},
              {name: 'processo', type: 'int'},
              {name: 'processo_codigo', type: 'string'},
              {name: 'processo_codigo_protocolo', type: 'string'},
              {name: 'referenciado', type: 'int'},
              {name: 'referenciado_codigo', type: 'string'},
              {name: 'referenciado_codigo_protocolo', type: 'string'},
              {name: 'tipo', type: 'int'},
              {name: 'tipo_display', type: 'string'},
              {name: 'descricao', type: 'string'},
            ]);

        return this._fields;
    }
});