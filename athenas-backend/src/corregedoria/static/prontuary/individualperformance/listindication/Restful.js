Ext._define('corregedoria.prontuary.individualperformance.listindication.Restful', {
    extend: 'core.Restful',

    resource: 'PRONTUARYDetailListIndication',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.prontuary.individualperformance.listindication.Restful.superclass.getFields.call(this, cfg).concat([
                {name: "icons"},
                {type: "bool", name: "active" },
                {type: "int", name: "list_figuration" },
                {type: "string", name: "edital" },
                {type: "int", name: "criteria" },
                {type: "date", name: "date_edital", dateFormat: "d/m/Y" },
            ]);

        return this._fields;
    }
});
