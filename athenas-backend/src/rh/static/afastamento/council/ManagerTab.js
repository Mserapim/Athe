
Ext._define('rh.afastamento.council.ManagerTab', {
    extend: 'rh.afastamento.ManagerTab',

    getGrid: function(args) {
        if(!this._grid)
            this._grid = Ext._create('rh.afastamento.council.ManagerGrid', {
                title: 'Afastamentos',
                department: args.department,
                region: 'center'
            });
        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};
        rh.afastamento.council.ManagerTab.superclass.constructor.call(this, cfg);
    }
});
