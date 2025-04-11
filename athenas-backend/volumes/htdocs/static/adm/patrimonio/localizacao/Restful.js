/**
 *
 **/
Ext._define('adm.patrimonio.localizacao.Restful', {
    extend: 'core.Restful',

    resource: 'PATLocalizacao',

    getFields: function() {
        return adm.patrimonio.localizacao.Restful.superclass.getFields.call(this).concat([
            {name: 'titulo', type: 'string'},
            {name: 'dentro_de_unicode', type: 'string'},
            {name: 'dentro_de', type: 'int'},
            {name: 'lotacao_relacionada_unicode', type: 'string'},
            {name: 'lotacao_relacionada', type: 'int', useNull: false},
            {name: 'endereco', type: 'string'},
            {name: 'ativo', type: 'bool'}
        ]);
    }
});
