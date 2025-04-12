Ext._define('rh.afastamento.afastamentorecessoforense.Restful', {
    extend: 'rh.afastamento.afastamento.Restful',
    resource: 'AFAAfastamentoRecessoForenseRestful',

    constructor: function(cfg) {
        rh.afastamento.afastamentorecessoforense.Restful.superclass.constructor.call(this, cfg);
    },

    getFields: function() {
        if(!this._fields){
            this._fields = rh.afastamento.afastamentorecessoforense.Restful.superclass.getFields.call(this, {}).concat([
                {type: "date", name: "data_inicio"},
                {type: "date", name: "data_fim"},
            ]);
        }
        
        return this._fields;
    }

});
