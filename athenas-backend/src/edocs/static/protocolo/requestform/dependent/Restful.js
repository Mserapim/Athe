Ext._define('edocs.protocolo.requestform.dependent.Restful', {
    extend: 'core.Restful',

    resource: 'RequestFormDependent',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = edocs.protocolo.requestform.dependent.Restful.superclass.getFields.call(this, cfg).concat([
                {name: "content_type", type: "int", useNull: true},
                {name: "content_type_unicode", type: "string"},
                {name: "object_id", type: "string"},
                {name: "name", type: "string"},
                {name: "cpf", type: "string"},
                {name: "degree_of_kinship", type: "string"},
                {name: "degree_of_kinship_display", type: "string"},
                {name: "unimpeded_as_taxpayer_dependent", type: "bool"}
            ]);

        return this._fields;
    }
});
