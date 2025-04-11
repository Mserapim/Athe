Ext._define('raf.searchprocessnumber.Restful', {
    extend: 'core.Restful',

    resource: 'RAFSearchProcessNumber',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = raf.searchprocessnumber.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "string", name: "data_processo", },
                {type: "string", name: "data_raf", },
                {type: "integer", name: "autoreference_id", },
                {type: "integer", name: "autoreference_source_add", },
                {type: "bool", name: "autoreference_is_adjustment", },
            ]);
        return this._fields;
    }

});
