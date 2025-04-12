Ext._define('rh.gfp.conference.liquidvalue.Restful', {
    extend: 'core.Restful',

    resource: 'GFPConferenceLiquidValue',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.gfp.conference.liquidvalue.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "folha", useNull: true},
                {type: "string", name: "folha_unicode"},
                {type: "int", name: "servidor", useNull: true},
                {type: "string", name: "servidor_unicode"},
                {type: "float", name: "total_liquido", useNull: true},
                {type: "float", name: "total_liquido_lancamentos", useNull: true},
            ]);

        return this._fields;
    }
});
