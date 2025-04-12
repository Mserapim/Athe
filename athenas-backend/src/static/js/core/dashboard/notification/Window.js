Ext._define('core.dashboard.notification.Window', {
    extend: 'Ext.Window',

    getTilePagePanel: function(cfg) {
        if(this._contentTilePanel) {
            return this._contentTilePanel
        }

        this._contentTilePanel = Ext._create('core.TilePagePanel', {
            papperModel: 'card',
            minWidth: 810,
            maxWidth: 810,
            width: 810,
            split: true,
        });

        this._contentTilePanel.setPageContent(cfg.message);

        return this._contentTilePanel;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            message: 'Nenhuma mensagem disponível',
            title: 'Notificação',
            width: 666,
            height: 584,
            buttonAlign: 'center',
        });

        Ext.apply(cfg, {
            modal: true,
            layout: 'fit',
            items: this.getTilePagePanel(cfg),
            buttons: [{
                text: 'OK',
                scope: this,
                handler: function () {
                    this.destroy();
                }
            }],
        });

        core.dashboard
          .notification
          .Window
          .superclass
          .constructor
          .call(this, cfg);
    },
});
