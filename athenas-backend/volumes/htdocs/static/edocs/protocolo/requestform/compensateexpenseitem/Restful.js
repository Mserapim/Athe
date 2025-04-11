Ext._define('edocs.protocolo.requestform.compensateexpenseitem.Restful', {
    extend: 'core.Restful',

    resource: 'RequestCompensateExpenseItem',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = edocs.protocolo.requestform.compensateexpenseitem.Restful.superclass.getFields.call(this, cfg).concat([
                {name: "compensate_item", type: "int", useNull: true},
                {name: "compensate_item_unicode", type: "string"},
                { type: "string", name: "nota" },
                { type: "textfield", name: "company" },
                { type: "date", name: "venc_date_nf", dateFormat: "d/m/Y" },
                { type: "bool", name: "nota_material" },
                { type: "bool", name: "nota_service" },
                { type: "float", name: "value" }
            ]);

        return this._fields;
    }
});
