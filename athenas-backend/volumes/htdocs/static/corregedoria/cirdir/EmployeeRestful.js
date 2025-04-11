Ext._define('corregedoria.cirdir.EmployeeRestful', {
    extend: 'rh.employee.Restful',

    resource: 'CIRDIREmployee',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.cirdir.EmployeeRestful.superclass.getFields.call(this, cfg).concat([
                
            ]);

        return this._fields;
    }

});
