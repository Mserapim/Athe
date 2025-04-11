/**
 *
 **/
Ext._define('adm.patrimonio.avaliacao.Restful', {
    extend: 'core.Restful',

    resource: 'PATAvaliacao',

    getFields: function() {
        if(!this._fields)
            this._fields = adm.patrimonio.avaliacao.Restful.superclass.getFields.call(this).concat([
                {name: 'icons', type: 'auto'},
                {name: 'tipo', type: 'int'},
                {name: 'tipo_display', type: 'string'},
                {name: 'competencia', type: 'string'},
                {name: 'number_formated', type: 'string'},
                {name: 'numero', type: 'int'},
                {name: 'ano', type: 'int'},
                {name: 'mes', type: 'int'},
                {name: 'tabela', type: 'int'},
                {name: 'tabela_unicode', type: 'string'},
                {name: 'executor', type: 'int'},
                {name: 'executor_unicode', type: 'string'},
                {name: 'de', type: 'date', dateFormat: 'd/m/Y H:i'},
                {name: 'ate', type: 'date', dateFormat: 'd/m/Y H:i'}
            ]);

        return this._fields;
    }
});
