Ext._define('corregedoria.inspection.inspection.filling.regularityofservices.bookofregisteroutcourtlawsuitcontrol.Restful', {
    extend: 'core.Restful',

    resource: 'INSPECTIONBookOfRegisterOutCourtLawsuitControl',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.inspection.inspection.filling.regularityofservices.bookofregisteroutcourtlawsuitcontrol.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "string", name: "book"},
                {type: "date", name: "opening_date", dateFormat: "d/m/Y"},
            ]);

        return this._fields;
    }
});
