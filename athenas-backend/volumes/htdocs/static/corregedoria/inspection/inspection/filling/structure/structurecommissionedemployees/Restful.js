Ext._define('corregedoria.inspection.inspection.filling.structure.structurecommissionedemployees.Restful', {
    extend: 'core.Restful',

    resource: 'INSPECTIONStructureCommissionedEmployees',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.inspection.inspection.filling.structure.structurecommissionedemployees.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "string", name: "sce_employee_unicode"},
                {type: "string", name: "sce_occupation_unicode"},
            ]);

        return this._fields;
    }
});
