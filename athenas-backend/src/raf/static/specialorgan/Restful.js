Ext._define('raf.specialorgan.Restful', {
    extend: 'core.Restful',

    resource: 'RAFSpecialOrgan',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = raf.autoreference.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "integer", name: "location", useNull: false,},,
                {type: "string", name: "location_unicode", },
            ]);

        return this._fields;
    }
});
