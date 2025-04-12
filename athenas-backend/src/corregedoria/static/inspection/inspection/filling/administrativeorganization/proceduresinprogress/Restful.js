Ext._define('corregedoria.inspection.inspection.filling.administrativeorganization.proceduresinprogress.Restful', {
    extend: 'core.Restful',

    resource: 'INSPECTIONAdministrativeOrganizationProceduresInProgress',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.inspection.inspection.filling.administrativeorganization.proceduresinprogress.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "string", name: "number"},
                {type: "date", name: "instauration_date", dateFormat: "d/m/Y"},
                {type: "string", name: "taxonomy_class"},
                {type: "string", name: "taxonomy_class_title"},
                {type: "string", name: "taxonomy_matter"},
                {type: "string", name: "taxonomy_matter_title"},
                {type: "string", name: "matter"},
                {type: "string", name: "observation"},
            ]);

        return this._fields;
    }
});
