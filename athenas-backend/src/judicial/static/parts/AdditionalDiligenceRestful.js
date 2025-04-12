
Ext._define('judicial.parts.AdditionalDiligenceRestful', {
    extend: 'judicial.PartLawsuitRestful',

    resource: 'EjudAdditionalDiligence',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = judicial.parts.AdditionalDiligenceRestful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "string",
                    name: "justification"
                }
            ]);

        return this._fields;
    }
});
