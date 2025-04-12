/**
 *
 **/
Ext._define('rh.falta.employee.Restful', {
    extend: 'core.Restful',

    resource: 'PONTFaltaEmployeeRestful',

    getFields: function () {
        var fields = rh.falta.employee.Restful.superclass.getFields.call(this);
        return fields.concat([
            { name: 'servidor_pk', type: 'pk' },
            { name: 'ativo', type: 'bool' },
            { name: 'matricula', type: 'int' },
            { name: 'pessoa_fisica_unicode', type: 'string' },
            { name: 'type_by_possession_display', type: 'string' },
            { name: 'departure_unicode', type: 'string' },
            { name: 'effective_unicode', type: 'string' },
            { name: 'commission_unicode', type: 'string' },
            { name: 'last_sendindg_time_sheet', type: 'string' },
            { name: 'status', type: 'string' },
            { name: 'in_telework', type: 'string' },
            { name: 'servidor_created_by_unicode', type: 'string', useNull: true },
            { name: 'servidor_created_at', type: 'date', dateFormat: 'd/m/Y H:i' },
            { name: 'servidor_modified_by_unicode', type: 'string', useNull: true },
            { name: 'servidor_modified_at', type: 'date', dateFormat: 'd/m/Y H:i' },
            { name: 'dt_posse', type: 'date', dateFormat: 'd/m/Y' },
        ]);
    }
});
