Ext._define('corregedoria.inspection.inspection.filling.procuratorate.proceduralmovementreturned.Restful', {
    extend: 'core.Restful',

    resource: 'INSPECTIONProceduralMovementReturned',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.inspection.inspection.filling.procuratorate.proceduralmovementreturned.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "year"},
                {type: "auto", name: "amount_january"},
                {type: "auto", name: "amount_february"},
                {type: "auto", name: "amount_march"},
                {type: "auto", name: "amount_april"},
                {type: "auto", name: "amount_may"},
                {type: "auto", name: "amount_june"},
                {type: "auto", name: "amount_july"},
                {type: "auto", name: "amount_august"},
                {type: "auto", name: "amount_september"},
                {type: "auto", name: "amount_october"},
                {type: "auto", name: "amount_november"},
                {type: "auto", name: "amount_december"},
                {type: "auto", name: "sum_amount"},
            ]);

        return this._fields;
    }
});
