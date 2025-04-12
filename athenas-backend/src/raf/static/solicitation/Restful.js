Ext._define('raf.solicitation.Restful', {
    extend: 'core.Restful',

    resource: 'RAFSolicitation',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = raf.autoreference.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "integer", name: "raf", useNull: false,},
                {type: "string", name: "raf_unicode", },
                {type: "string", name: "unicode", },
                {type: "int", name: "pk", },
            ]);

        return this._fields;
    }
});
