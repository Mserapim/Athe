Ext._define('corregedoria.cirdir.teaching.institution.Restful', {
    extend: 'core.Restful',

    resource: 'CIRDIRInstitution',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.cirdir.teaching.institution.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "institution" },
                {type: "string", name: "razao_social" },
                {type: "string", name: "cnpj" },
                {type: "int", name: "county" },
                {type: "string", name: "county_unicode" },
                {type: "string", name: "nome" }
            ]);

        return this._fields;
    }
});
