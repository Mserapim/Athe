/**
 *
 **/
Ext._define('adm.patrimonio.avaliacao.ItemRestful', {
    extend: 'core.Restful',

    resource: 'PATItemAvaliacao',

    getFields: function() {
        if(!this._fields)
            this._fields = adm.patrimonio.avaliacao.Restful.superclass.getFields.call(this).concat([
                {name: 'icons', type: 'auto'},
                {name: 'patrimonio', type: 'int'},
                {name: 'patrimonio_unicode', type: 'string'},
                {name: 'especie', type: 'int'},
                {name: 'especie_unicode', type: 'string'},
                {name: 'plaqueta', type: 'string'},
                {name: 'valor_atual', type: 'float', useNull: true},
                {name: 'valor_avaliado', type: 'float', useNull: true},
                {name: 'depreciacao', type: 'float', useNull: true},
                {name: 'residual', type: 'float', useNull: true},
                {name: 'quantidade_dias', type: 'int', useNull: true},
                {name: 'vida_util', type: 'int', useNull: true},
                {name: 'conservacao', type: 'int', useNull: true},
                {name: 'conservacao_display', type: 'string'},
                {name: 'data_tombo', type: 'date', dateFormat: 'd/m/Y H:i'},
                {name: 'custo_aquisicao', type: 'float', useNull: true},
                {name: 'discarded', type: 'bool'},
                {name: 'discarded_at', type: 'date', dateFormat: 'd/m/Y H:i'},
                {name: 'discarded_by', type: 'int', useNull: true},
                {name: 'discarded_by_unicode', type: 'string'},
                {name: 'discarded_justify', type: 'string'},
            ]);

        return this._fields;
    }
});
