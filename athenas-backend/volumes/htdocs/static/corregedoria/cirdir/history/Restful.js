Ext._define('corregedoria.cirdir.history.Restful', {
    extend: 'core.Restful',

    resource: 'CIRDIRHistory',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.cirdir.history.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "date", name: "dt_action", dateFormat: 'd/m/Y H:i:s' },
                {type: "string", name: "action" },
                {type: "string", name: "employee_unicode" },
            ]);

        return this._fields;
    }
});
