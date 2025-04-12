/**
 *
 **/
Ext._define('rh.pesquisa.EscolaridadeRestful', {
    'extend': 'core.Restful',

    'resource': 'RHCensoEstudo',

    'getFields': function() {
        var fields = rh.pesquisa.EscolaridadeRestful.superclass.getFields.call(this);

        return fields.concat([
            {'name': 'servidor_unicode', 'type': 'string'},
            {'name': 'servidor', 'type': 'int'},
            {'name': 'cidade_unicode', 'type': 'string'},
            {'name': 'cidade', 'type': 'int'},
            {'name': 'nivel_escolaridade_display', 'type': 'string'},
            {'name': 'nivel_escolaridade', 'type': 'int'},
            {'name': 'instituicao', 'type': 'string'},
            {'name': 'curso', 'type': 'string'},
            {'name': 'ano_conclusao', 'type': 'int'},
        ]);
    }
});
