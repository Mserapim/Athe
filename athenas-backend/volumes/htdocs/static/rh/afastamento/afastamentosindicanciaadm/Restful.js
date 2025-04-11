Ext._define('rh.afastamento.afastamentosindicanciaadm.Restful', {
    extend: 'rh.afastamento.afastamento.Restful',
    resource: 'AFAAfastamentoSindicanciaAdmRestful',

    constructor: function(cfg) {
        rh.afastamento.afastamentosindicanciaadm.Restful.superclass.constructor.call(this, cfg);
    },

    getFields: function() {
        if(!this._fields){
            this._fields = rh.afastamento.afastamentosindicanciaadm.Restful.superclass.getFields.call(this, {}).concat([
                {type: "int", name: "prazo_dias", useNull: true},
            ]);
        }
        return this._fields;
    }
});
