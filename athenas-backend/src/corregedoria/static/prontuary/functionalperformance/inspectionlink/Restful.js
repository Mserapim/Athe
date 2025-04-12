Ext._define('corregedoria.prontuary.functionalperformance.inspectionlink.Restful', {
    extend: 'core.Restful',

    resource: 'PRONTUARYInspectionLink',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.prontuary.functionalperformance.inspectionlink.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "bool", name: "active" },
                {type: "string", name: "inspection_execution_organ" },
                {type: "string", name: "inspection_date_initial" },
                {type: "string", name: "inspection_date_final" },
            ]);

        return this._fields;
    }
});
