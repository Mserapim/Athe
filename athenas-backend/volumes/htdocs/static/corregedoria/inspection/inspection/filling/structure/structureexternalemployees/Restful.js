Ext._define('corregedoria.inspection.inspection.filling.structure.structureexternalemployees.Restful', {
    extend: 'core.Restful',

    resource: 'INSPECTIONStructureExternalEmployees',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.inspection.inspection.filling.structure.structureexternalemployees.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "string", name: "see_employee_unicode"},
                {type: "string", name: "see_occupation_unicode"},
                {type: "string", name: "see_category"},
            ]);

        return this._fields;
    }
});
