 Ext._define("rh.gfp.gcpp_est_res.Restful", {
    extend: 'core.Restful',

    resource: 'GfpGCPPEstResRestful',

    getFields: function() {
        if(!this._fields){
            this._fields = rh.gfp.gcpp_est_res.Restful.superclass.getFields.call(this, {}).concat([
                {type: "string", name: "servidor_unicode", useNull: true},
                {type: "auto", name: "icons"},
                {type: "string", name: "verba"},
                {type: "string", name: "qtd_dias_confirmado"},
                {type: "string", name: "qtd_dias_calculado"},
                {type: "string", name: "valor_calculado"},
                {type: "string", name: "qtd_dias_pgto"},
                {type: "string", name: "valor_pgto"},
                {type: "string", name: "pct"},
                {type: "string", name: "periodo"},
                {type: "string", name: "conferido_em"},
                {type: "string", name: "conferido_por"},
                {type: "string", name: "ref_falta"},
                {type: "string", name: "modified_by_unicode"},
            ]);
        }
        return this._fields;
    }
});