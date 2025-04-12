Ext._define('raf.autoreference.Restful', {
    extend: 'core.Restful',

    resource: 'RAFAutoReference',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = raf.autoreference.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "integer", name: "activity", useNull: false,},
                {type: "integer", name: "autoreference_id", },
                {type: "string", name: "activity_unicode", },
                {type: "string", name: "process_number", },
                {type: "string", name: "source", },
                {type: "string", name: "source_add", },
                {type: "string", name: "source_add_display", },
                {type: "bool", name: "is_adjustment", },
                {type: "bool", name: "removed", },
                {type: "date", name: "date", dateFormat: "d/m/Y H:i", },
            ]);

        return this._fields;
    }
});
