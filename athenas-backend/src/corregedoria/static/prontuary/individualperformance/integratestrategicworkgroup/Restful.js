Ext._define('corregedoria.prontuary.individualperformance.integratestrategicworkgroup.Restful', {
    extend: 'core.Restful',

    resource: 'PRONTUARYDetailIntegrateStrategicWorkGroup',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.prontuary.individualperformance.integratestrategicworkgroup.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "score" },
                {type: "string", name: "workgroup" },
            ]);

        return this._fields;
    }
});
