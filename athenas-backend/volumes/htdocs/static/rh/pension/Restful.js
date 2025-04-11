/**
 *
 **/
Ext._define('rh.pension.Restful', {
    extend: 'core.Restful',

    resource: 'PENPension',

    getFields: function() {
        var fields = rh.pension.Restful.superclass.getFields.call(this);
        return fields.concat([
            {name: 'servidor', type: 'int'},
            {name: 'servidor_unicode', type: 'string'},
            {name: 'pensionista', type: 'int'},
            {name: 'pensionista_unicode', type: 'string'},
            {name: 'representante_legal', type: 'int'},
            {name: 'representante_legal_unicode', type: 'string'},
            {name: 'publicacao', type: 'int'},
            {name: 'publicacao_unicode', type: 'string'},
            {name: 'active', type: 'bool'},
            {name: 'data_inicio', type: 'date', dateFormat: 'd/m/Y'},
            {name: 'data_fim', type: 'date', dateFormat: 'd/m/Y'},
            {name: 'tipo', type: 'int'},
            {name: 'tipo_display', type: 'int'},
            {name: 'valor', type: 'decimal'},
            {name: 'kind', type: 'string'},
            {name: 'event_employee', type: 'int'},
            {name: 'event_employee_unicode', type: 'string'},
            {name: 'event_employee_13', type: 'int'},
            {name: 'event_employee_13_unicode', type: 'string'},
            {name: 'event_pensioner', type: 'int'},
            {name: 'event_pensioner_unicode', type: 'string'},
            {name: 'type_of_pension', type: 'int'},
            {name: 'type_of_pension_display', type: 'string'},
        ]);
    }
});