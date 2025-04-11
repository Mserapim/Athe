Ext._define('corregedoria.prontuary.individualperformance.integrateworkgroup.Restful', {
    extend: 'core.Restful',

    resource: 'PRONTUARYDetailIntegrateWorkGroup',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.prontuary.individualperformance.integrateworkgroup.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "score" },
                {type: "string", name: "workgroup" },
            ]);

        return this._fields;
    }
});
