Ext._define('corregedoria.prontuary.functionalperformance.listcumulation.Restful', {
    extend: 'core.Restful',

    resource: 'PRONTUARYListCumulation',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.prontuary.functionalperformance.listcumulation.Restful.superclass.getFields.call(this, cfg).concat([
                {name: "icons"},
                {type: "int", name: "pk" },
                {type: "bool", name: "active" },
                {type: "string", name: "cumulation_date_initial" },
                {type: "string", name: "cumulation_date_final" },
                {type: "int", name: "total_days" },
            ]);

        return this._fields;
    }
});
