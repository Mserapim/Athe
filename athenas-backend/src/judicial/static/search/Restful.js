Ext._define('judicial.search.Restful', {
    extend: 'judicial.PartLawsuitRestful',

    resource: 'EJudPartLawsuitSearch',

    getFields: function (cfg) {
        if (!this._fields)
            this._fields = judicial.search.Restful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "string",
                    name: "lawsuit_location_unicode"
                }
            ]);

        return this._fields;
    }
});
