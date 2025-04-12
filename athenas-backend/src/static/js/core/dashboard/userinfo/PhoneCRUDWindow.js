Ext._define('core.dashboard.userinfo.PhoneCRUDWindow', {
    extend: 'Ext.Window',

    getPhoneGrid: function (cfg) {
        if (this._phoneGrid) {
            return this._phoneGrid;
        }

        this._phoneGrid = Ext._create('rh.telefone.byUser.Grid');

        return this._phoneGrid;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Atualização de telefones',
            width: 675,
            height: 320,
            modal: true,
            border: false,
        });

        Ext.apply(cfg, {
            layout: 'fit',
            items: [
                this.getPhoneGrid(cfg),
            ],
        });

        core.dashboard
          .userinfo
          .PhoneCRUDWindow
          .superclass
          .constructor
          .call(this, cfg);
    },
});
