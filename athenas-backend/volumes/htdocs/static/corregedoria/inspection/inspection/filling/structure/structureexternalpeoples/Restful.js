Ext._define('corregedoria.inspection.inspection.filling.structure.structureexternalpeoples.Restful', {
    extend: 'core.Restful',

    resource: 'INSPECTIONStructureExternalPeoples',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.inspection.inspection.filling.structure.structureexternalpeoples.Restful.superclass.getFields.call(this, cfg).concat([
                // {type: "string", name: "sep_employee_unicode"},
                // {type: "string", name: "sep_occupation_unicode"},
                // {type: "string", name: "sep_category"},
                {type: "string", name: "name"},
                {type: "string", name: "function"},
                {type: "string", name: "category"},
            ]);

        return this._fields;
    }
});
