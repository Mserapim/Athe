Ext._define('corregedoria.cirdir.irscode.Restful', {
    extend: 'core.Restful',

    resource: 'CIRDIRIRSCode',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.cirdir.irscode.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "code" },
                {type: "string", name: "title" },
                {type: "int", name: "type_irscode" },
                {type: "string", name: "type_irscode_unicode" },
            ]);

        return this._fields;
    }
});
