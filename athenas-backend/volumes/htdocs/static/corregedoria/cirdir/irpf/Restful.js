Ext._define('corregedoria.cirdir.irpf.Restful', {
    extend: 'core.Restful',

    resource: 'CIRDIRIrpf',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.cirdir.irpf.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "file" },
                {type: "string", name: "title" },
                {type: "auto", name: "created_at" },
                {type: "int", name: "controlinformation" },
                {type: "int", name: "of_who" },
            ]);

        return this._fields;
    }
});
