Ext._define('corregedoria.linkinspectionraf.Restful', {
    extend: 'core.Restful',

    resource: 'CORREGEDORIALinkInspectionRAF',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.linkinspectionraf.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "inspection_table"},
                {type: "string", name: "inspection_table_display"},
                {type: "int", name: "raf_item", useNull: true},
                {type: "string", name: "raf_item_unicode"},
                {type: "int", name: "raf_subitem"},
                {type: "string", name: "raf_subitem_unicode"},
                {type: "string", name: "raf_quiz"},
            ]);

        return this._fields;
    }
});
