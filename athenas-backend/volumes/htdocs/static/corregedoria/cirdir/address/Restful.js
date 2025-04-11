Ext._define('corregedoria.cirdir.address.Restful', {
    extend: 'core.Restful',

    resource: 'CIRDIRAddress',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.cirdir.address.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "type_residence" },
                {type: "int", name: "ref_address" },
                {type: "string", name: "ref_address_unicode" },
                {type: "date", name: "start_date", dateFormat: "d/m/Y"},
                {type: "date", name: "end_date", dateFormat: "d/m/Y"},
                {type: "bool", name: "authorization_reside_outside" },
                {type: "auto", name: "icons" },
                {type: "auto", name: "datetime" },
            ]);

        return this._fields;
    }
});
