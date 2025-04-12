Ext._define('rh.employee.trainee.Restful', {
    extend: 'rh.employee.CollaboratorRestful',
    resource: 'RHTrainee',

    getFields: function() {
        var fields = rh.employee.trainee.Restful.superclass.getFields.call(this).concat([
            {name: 'employee_supervisor', type: 'int'},
            {name: 'employee_supervisor_unicode', type: 'string'},
            {name: 'educational_institution', type: 'int'},
            {name: 'educational_institution_unicode', type: 'string'},
            {name: 'integration_agent', type: 'int'},
            {name: 'integration_agent_unicode', type: 'string'},
            {name: 'nature', type: 'int'},
            {name: 'level', type: 'int'},
            {name: 'occupation_area', type: 'string'},
            {name: 'insurance_number', type: 'string'},
            {name: 'value', type: 'string'},
        ]);
        return fields;
    }
});
