/**
 *
 **/
Ext._define('rh.gfp.evento.EventoRestful', {
    extend: 'core.Restful',

    resource: 'GFPEventoRestful',

    remote: false,

    getFields: function() {
        var fields = rh.gfp.evento.EventoRestful.superclass.getFields.call(this);
        return fields.concat([
            {name: 'numero', type: 'string'},
            {name: 'titulo', type: 'string'},
            {name: 'lancamento', type: 'string'},
            {name: 'lancamento_display', type: 'string'},
            {name: 'tipo', type: 'string'},
            {name: 'tipo_display', type: 'string'},
            {name: 'tipo_calculo', type: 'int', useNull: true},
            {name: 'tipo_calculo_display', type: 'string'},
            {name: 'automatico', type: 'boolean'},
            {name: 'calculo', type: 'int', useNull: true},
            {name: 'calculo_unicode', type: 'string'},
            {name: 'aplica_consignado', type: 'boolean'},
            {name: 'aplica_consignavel', type: 'boolean'},
            {name: 'calculo_invertido', type: 'boolean'},
            {name: 'incide_sobre', type: 'auto'},
            {name: 'quantidade', type: 'auto'},
            {name: 'quantidade_max', type: 'auto'},
            {name: 'porcentagem', type: 'auto'},
            {name: 'valor_base', type: 'auto'},
            {name: 'teto', type: 'auto'},
            {name: 'piso', type: 'auto'},
            {name: 'config_transparencia', type: 'int', useNull: true},
            {name: 'base_de_calculo', type: 'int', useNull: true},
            {name: 'carater', type: 'int', useNull: true},
            {name: 'carater_display', type: 'string'},
            {name: 'consignatario', type: 'int'},
            {name: 'publicacao', type: 'int'},

        ]);
    }
});
