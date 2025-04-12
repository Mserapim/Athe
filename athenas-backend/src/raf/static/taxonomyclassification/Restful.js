Ext._define('raf.taxonomyclassification.Restful', {
    extend: 'core.Restful',

    resource: 'RAFTaxonomyClassification',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = raf.taxonomyclassification.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "string", name: "cnmp_code"},
                {type: "string", name: "title"},
                {type: "string", name: "unicode"},
                {type: "integer", name: "item", useNull: true},
                {type: "string", name: "item_unicode"},
                {type: "integer", name: "subitem", useNull: true},
                {type: "string", name: "subitem_unicode"},
                {type: "integer", name: "classification", useNull: true},
                {type: "string", name: "classification_unicode"},
                {type: "integer", name: "exclude_classification", useNull: true},
                {type: "string", name: "exclude_classification_unicode"},

            ]);

        return this._fields;
    }
});
