/**
 *
 **/
Ext._define('adm.patrimonio.avaliacao.ParametroRestful', {
    extend: 'core.Restful',

    resource: 'PATParametroAvaliacao',

    getFields: function() {
        if(!this._fields)
            this._fields = adm.patrimonio.avaliacao.ParametroRestful.superclass.getFields.call(this).concat([
                {name: 'variavel', type: 'int'},
                {name: 'variavel_display', type: 'string'},
                {name: 'tipo', type: 'int'},
                {name: 'tabela', type: 'int'},
                {name: 'tabela_unicode', type: 'string'},
                {name: 'valor', type: 'int'}
            ]);

        return this._fields;
    }
});
