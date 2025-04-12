Ext._define('raf.activity.Restful', {
    extend: 'core.Restful',

    resource: 'RAFActivity',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = raf.activity.Restful.superclass.getFields.call(this, cfg).concat([
                {name:'icons'},
                {name:'subitem_typeicons'},
                {type: "string", name: "workerlocation_unicode"},
                {type: "integer", name: "workerlocation", useNull: true},
                {type: "string", name: "item_unicode"},
                {type: "integer", name: "item", useNull: true},
                {type: "string", name: "subitem_unicode"},
                {type: "string", name: "subitem_description"},
                {type: "integer", name: "subitem", useNull: true},
                {type: "integer", name: "amount_submitted", useNull: true},
                {type: "integer", name: "amount_athenas", useNull: true},
            ]);

        return this._fields;
    }
});
