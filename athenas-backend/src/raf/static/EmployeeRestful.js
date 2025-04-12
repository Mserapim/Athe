Ext._define('raf.EmployeeRestful', {
    extend: 'rh.employee.Restful',

    resource: 'RAFEmployee',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = raf.EmployeeRestful.superclass.getFields.call(this, cfg).concat([
                {
                  type: 'string',
                  name: 'first_adjustment_date',
                  // dateFormat: 'd/m/Y H:i',
                 },
                 {
                   type: 'auto',
                   name: 'locations_follow',
                  },
            ]);

        return this._fields;
    }

});
