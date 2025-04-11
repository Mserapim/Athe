Ext._define('corregedoria.inspection.inspection.filling.administrativeorganization.existingregisters.Restful', {
    extend: 'core.Restful',

    resource: 'INSPECTIONExistingRegisters',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.inspection.inspection.filling.administrativeorganization.existingregisters.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "string", name: "register"},
                {type: "int", name: "registration_type"},
                {type: "string", name: "registration_type_display"},
            ]);

        return this._fields;
    }
});
