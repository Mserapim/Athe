/**
 *
 **/
Ext._define('rh.employee.Restful', {
    extend: 'core.Restful',

    resource: 'RHEmployeeRestful',

    getFields: function () {
        var fields = rh.employee.Restful.superclass.getFields.call(this);
        return fields.concat([
            { name: 'pk', type: 'pk' },
            { type: 'bool', name: 'ativo' },
            { name: 'user', type: 'int' },
            { name: 'user_unicode', type: 'string' },
            { name: 'tipo', type: 'string' },
            { name: 'pessoa_fisica', type: 'int' },
            { name: 'pessoa_fisica_unicode', type: 'string' },
            { name: 'social_name', type: 'string' },
            { name: 'email', type: 'string' },
            { name: 'matricula', type: 'int' },
            { name: 'vpi', type: 'decimal' },
            { name: 'data_referencia_ferias', type: 'date', dateFormat: 'd/m/Y' },
            { name: 'chefe_imediato', type: 'int' },
            { name: 'chefe_imediato_unicode', type: 'string' },
            { name: 'effective_unicode', type: 'string' },
            { name: 'commission_unicode', type: 'string' },
            { name: 'elective_unicode', type: 'string' },
            { type: 'string', name: 'departure_unicode' },
            { name: 'data_exercicio', type: 'date', dateFormat: 'd/m/Y' },
            { name: 'data_posse', type: 'date', dateFormat: 'd/m/Y' },
            { name: 'data_desligamento', type: 'date', dateFormat: 'd/m/Y' },
            { type: 'date', name: 'created_at', dateFormat: 'd/m/Y H:i' },
            { type: 'date', name: 'modified_at', dateFormat: 'd/m/Y H:i' },
            { type: 'string', name: 'created_by_unicode', useNull: true },
            { type: 'string', name: 'modified_by_unicode', useNull: true },
            { type: 'string', name: 'type_by_possession_display' },
            { type: 'int', name: 'category_esocial' },
            { type: 'string', name: 'category_esocial_display' },
            { type: 'int', name: 'event_esocial' },
            { type: 'string', name: 'unicode_status', useNull: true },
        ]);
    }
});
