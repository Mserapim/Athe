/**
 *
 **/
Ext._define('rh.employee.CollaboratorRestful', {
    extend: 'rh.employee.Restful',

    resource: 'RHCollaboratorRestful',

    getFields: function() {
        var fields = rh.employee.CollaboratorRestful.superclass.getFields.call(this);
        return fields.concat([
            {name: 'date_born', type: 'date', dateFormat: 'd/m/Y'},
            {name: 'cpf', type: 'string'},
        ]);
    }
});