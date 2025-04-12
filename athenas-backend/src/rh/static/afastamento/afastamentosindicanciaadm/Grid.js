Ext._define('rh.afastamento.afastamentosindicanciaadm.Grid', {
    extend: 'rh.afastamento.afastamento.Grid',
    restWindow: 'rh.afastamento.afastamentosindicanciaadm.Window',

    constructor: function(cfg) {
        rh.afastamento.afastamentosindicanciaadm.Grid.superclass.constructor.call(this, cfg);
    },

    getColumnModelItems: function(){
        if(!this._columnModelItems){
            this._columnModelItems = rh.afastamento.afastamentosindicanciaadm.Grid.superclass.getColumnModelItems.call(
                this, {});
            this._columnModelItems = this._columnModelItems.concat([
                {header: 'Dias', dataIndex: 'prazo_dias', width: 120, hidden: false},
            ]);
        }
        return this._columnModelItems;
    }
});

core.RestfulGrid.register(
    'rh.afastamento.afastamentosindicanciaadm.Restful',
    'rh.afastamento.afastamentosindicanciaadm.Grid'
);

