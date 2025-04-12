/**
 *
 **/
Ext._define('rh.movimentacao.concession.Restful', {
    extend: 'rh.movimentacao.pessoal.Restful',

    resource: 'RHConcessionMoveRestful',

    constructor: function(cfg) {
        rh.movimentacao.concession.Restful.superclass.constructor.call(this, cfg);
    },

    getFields: function() {
        if(!this._fields){
            this._fields = rh.movimentacao.concession.Restful.superclass.getFields.call(this, {});
        }
        return this._fields;
    }
});
