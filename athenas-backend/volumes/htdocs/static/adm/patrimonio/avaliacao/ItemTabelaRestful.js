/**
 *
 **/
Ext._define('adm.patrimonio.avaliacao.ItemTabelaRestful', {
    extend: 'core.Restful',

    resource: 'PATItemTabelaAvaliacao',

    getFields: function() {
        if(!this._fields)
            this._fields = adm.patrimonio.avaliacao.ItemTabelaRestful.superclass.getFields.call(this).concat([
                {name: 'tipo', type: 'int'},
                {name: 'tabela', type: 'int'},
                {name: 'tabela_unicode', type: 'string'},
                {name: 'grupo', type: 'int'},
                {name: 'grupo_unicode', type: 'string'},
                {name: 'especie', type: 'int', useNull: true, defaultValue: ''},
                {name: 'especie_unicode', type: 'string'},
                {name: 'vida_util', type: 'int'},
                {name: 'depreciacao', type: 'float'},
                {name: 'residual', type: 'float'}
            ]);

        return this._fields;
    }
});
