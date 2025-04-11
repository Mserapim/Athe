/**
 *
 **/
Ext._define('rh.pesquisa.PrevidenciarioRestful', {
    'extend': 'core.Restful',

    'resource': 'RHCensoPrevidenciario',

    'getFields': function() {
        var fields = rh.pesquisa.PrevidenciarioRestful.superclass.getFields.call(this);

        return fields.concat([
            {'name': 'servidor_unicode', 'type': 'string'},
            {'name': 'servidor', 'type': 'int'},
            {'name': 'tipo_regime_display', 'type': 'string'},
            {'name': 'tipo_regime', 'type': 'int'},
            {'name': 'empresa_orgao', 'type': 'string'},
            {"name": "data_inicio", 'type': 'string'},
            {"name": "data_fim", 'type': 'string'},
            {"name": "data_nascimento", 'type': 'string'},
            {'name': 'idade', 'type': 'int'},
            {'name': 'dias', 'type': 'int'},
        ]);
    }
});
