Ext._define('judicial.search.person.Restful', {
    extend: 'judicial.OutCourtLawsuitRestful',

    resource: 'EJudOutCourtLawsuitSearch',

    getFields: function (cfg) {
        if (!this._fields)
            this._fields = judicial.search.person.Restful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "string",
                    name: "lawsuit_location_unicode"
                },
                {
                    type: "string",
                    name: "interesteds"
                },
                {
                    type: "string",
                    name: "blokes"
                },
                {
                    type: 'string',
                    name: 'status'
                }
            ]);

        return this._fields;
    }
});
