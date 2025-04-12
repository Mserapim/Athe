Ext._define('corregedoria.inspection.inspection.filling.regularityofservices.bookofregistercourtlawsuitcontrol.Restful', {
    extend: 'core.Restful',

    resource: 'INSPECTIONBookOfRegisterCourtLawsuitControl',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.inspection.inspection.filling.regularityofservices.bookofregistercourtlawsuitcontrol.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "string", name: "book"},
                {type: "date", name: "opening_date", dateFormat: "d/m/Y"},
            ]);

        return this._fields;
    }
});
