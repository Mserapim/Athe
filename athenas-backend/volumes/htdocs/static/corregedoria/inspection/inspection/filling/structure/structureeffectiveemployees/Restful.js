Ext._define('corregedoria.inspection.inspection.filling.structure.structureeffectiveemployees.Restful', {
    extend: 'core.Restful',

    resource: 'INSPECTIONStructureEffectiveEmployees',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.inspection.inspection.filling.structure.structureeffectiveemployees.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "string", name: "sef_employee_unicode"},
                {type: "string", name: "sef_occupation_unicode"},
            ]);

        return this._fields;
    }
});
