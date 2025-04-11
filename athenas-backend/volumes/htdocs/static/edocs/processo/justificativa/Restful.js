/**
 *
 **/
Ext._define('edocs.processo.justificativa.Restful', {
    extend: 'core.Restful',

    resource: 'EpadJustificativa',

    getFields: function() {
        if(!this._fields)
            this._fields = edocs.processo.justificativa.Restful.superclass.getFields.call(this).concat([
              // Apenas para listar em uma Grid
              // {name: 'processo', type: 'int'},
              // {name: 'processo_codigo', type: 'string'},
              // {name: 'movimentacao', type: 'int'},
              // {name: 'usuario', type: 'string'},
              // {name: 'valor_antigo', type: 'int'},
              // {name: 'valor_novo', type: 'int'},
              // {name: 'tipo', type: 'int'},
              // {name: 'tipo_display', type: 'string'},
              // {name: 'justificativa', type: 'string'},
            ]);

        return this._fields;
    }
});