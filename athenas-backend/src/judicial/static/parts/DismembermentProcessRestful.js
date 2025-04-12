
Ext._define('judicial.parts.DismembermentProcessRestful', {
    extend: 'judicial.PartLawsuitRestful',

    resource: 'EjudDismembermentProcess',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = judicial.parts.DismembermentProcessRestful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "string",
                    name: "justification"
                },
                {
                    type: "string",
                    name: "change_title"
                }
            ]);

        return this._fields;
    }
});
