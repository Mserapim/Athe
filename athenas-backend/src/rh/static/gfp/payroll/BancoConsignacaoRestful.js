Ext._define('rh.gfp.payroll.BancoConsignacaoRestful', {
    extend: 'core.Restful',

    resource: 'GFPBancoConsignacao',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.gfp.payroll.BancoConsignacaoRestful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "id"}, 
                {type: "string", name: "nome"}, 
                {type: "string", name: "numero"}, 
                {type: "string", name: "agencia"}, 
                {type: "string", name: "dv_agencia"},
                {type: "string", name: "conta"},
                {type: "string", name: "dv_conta"}
            ]);

        return this._fields;
    }
});
