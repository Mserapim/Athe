Ext._define('corregedoria.inspection.inspection.filling.administrativeorganization.archivedprocedures.Restful', {
    extend: 'core.Restful',

    resource: 'INSPECTIONAdministrativeOrganizationArchivedProcedures',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.inspection.inspection.filling.administrativeorganization.archivedprocedures.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "string", name: "number"},
                {type: "date", name: "instauration_date", dateFormat: "d/m/Y"},
                {type: "date", name: "archived_date", dateFormat: "d/m/Y"},
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
