/**
 *
 **/
Ext._define('rh.employee.registration.Restful', {
    extend: 'rh.employee.specialized.Restful',

    resource: 'RHRegistration',

    getFields: function() {
        var fields = rh.employee.registration.Restful.superclass.getFields.call(this);
        return fields.concat([

        ]);
    }
});