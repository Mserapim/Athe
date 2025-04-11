Ext._define('rh.afastamento.afastamentoparcialestudar.Restful', {
    extend: 'rh.afastamento.afastamento.Restful',
    resource: 'AFAAfastamentoParcialEstudarRestful',

    constructor: function(cfg) {
        rh.afastamento.afastamentoparcialestudar.Restful.superclass.constructor.call(this, cfg);
    },

    getFields: function() {
        if(!this._fields){
            this._fields = rh.afastamento.afastamentoparcialestudar.Restful.superclass.getFields.call(this, {}).concat([
                {type: "int", name: "instituicao", useNull: true},
                {type: "string", name: "instituicao_unicode"},
                {type: "int", name: "curso", useNull: true},
                {type: "string", name: "curso_unicode"},
                {type: "int", name: "localidade", useNull: true},
                {type: "string", name: "localidade_unicode"},
                {type: "bool", name: "parcial"},
            ]);
        }
        return this._fields;
    }
});
