/**
 *
 **/
Ext._define('adm.patrimonio.avaliacao.TabelaRestful', {
    extend: 'core.Restful',

    resource: 'PATTabelaAvaliacao',

    getFields: function() {
        if(!this._fields)
            this._fields = adm.patrimonio.avaliacao.TabelaRestful.superclass.getFields.call(this).concat([
                {name: 'numero', type: 'int'},
                {name: 'ano', type: 'int'},
                {name: 'numero_formatado', type: 'string'},
                {name: 'data_vigencia', type: 'date', dateFormat: 'd/m/Y'},
                {name: 'data_fim_vigencia', type: 'date', dateFormat: 'd/m/Y'},
                {name: 'publicacao', type: 'int'},
                {name: 'publicacao_unicode', type: 'string'}
            ]);

        return this._fields;
    }
});
