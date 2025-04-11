/**
 *
 **/
Ext._define('rh.movimentacao.fired.retirement.Restful', {
    extend: 'rh.movimentacao.fired.Restful',

    resource: 'RHRetirementMoveRestful',

    constructor: function(cfg) {
        rh.movimentacao.fired.retirement.Restful.superclass.constructor.call(this, cfg);
    },

    getFields: function() {
        if(!this._fields){
            this._fields = rh.movimentacao.fired.retirement.Restful.superclass.getFields.call(this, {}).concat([
                {type: "int", name: "tipo_aposentadoria", useNull: true},
                {type: "string", name: "tipo_aposentadoria_display"},
                {type: "int", name: "reversao", useNull: true},
                {type: "string", name: "reversao_display"},
            ]);
        }
        return this._fields;
    }
});
