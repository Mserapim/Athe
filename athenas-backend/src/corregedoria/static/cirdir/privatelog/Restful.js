Ext._define('corregedoria.cirdir.privatelog.Restful', {
    extend: 'core.Restful',

    resource: 'CIRDIRPrivateLog',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.cirdir.privatelog.Restful.superclass.getFields.call(this, cfg).concat([
              {type: "string", name: "information" },
              {type: "date", name: "create", dateFormat: "d/m/Y H:i:s" },
            ]);

        return this._fields;
    }
});
