Ext._define('corregedoria.cirdir.property.Restful', {
    extend: 'core.Restful',

    resource: 'CIRDIRProperty',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.cirdir.property.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "string", name: "description" },
                {type: "int", name: "irscode" },
                {type: "string", name: "irscode_unicode" },
                {type: "int", name: "country" },
                {type: "string", name: "country_unicode" },
                {type: "int", name: "kind" },
                {type: "string", name: "kind_unicode" },
                {type: "float", name: "current_value" },
                {type: "float", name: "last_value" },
                {type: "auto", name: "icons" },

            ]);

        return this._fields;
    }
});
