Ext._define('rh.employee.retiree.Restful', {
    extend: 'rh.employee.CollaboratorRestful',
    resource: 'RHRetiree',

    getFields: function() {
        var fields = rh.employee.retiree.Restful.superclass.getFields.call(this).concat([
            {name: 'employee_supervisor', type: 'int'},
            {name: 'type_retirement', type: 'int'},
            {name: 'type_retirement_display', type: 'string'},
            {name: 'previous_type', type: 'string'},
            {name: 'previous_type_display', type: 'string'},
        ]);
        return fields;
    }
});
