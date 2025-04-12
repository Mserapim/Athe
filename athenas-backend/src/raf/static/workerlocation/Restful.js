Ext._define('raf.workerlocation.Restful', {
    extend: 'core.Restful',

    resource: 'RAFWorkerLocation',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = raf.workerlocation.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "integer", name: "location", useNull: true},
                {type: "string", name: "location_unicode"},
                {type: "integer", name: "raf", useNull: true},
                {type: "string", name: "raf_unicode"},
            ]);

        return this._fields;
    }
});
