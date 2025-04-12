/*
 *
 */
Ext._define('edocs.protocolo.SelectProtocolWindow', {
    extend: 'Ext.Window',

    getInboxPanel: function(cfg) {
        if(!this._inboxPanel) {
            this._inboxPanel = Ext._create('edocs.protocolo.box.MainGrid', {
                region: 'center',
                detailView: this.getTilePanel(cfg)
            });
        }

        return this._inboxPanel;
    },

    getTilePanel: function(cfg) {
        if(!this._tilePanel)
            this._tilePanel = Ext._create('core.TilePagePanel', {
                region: 'east',
                split: true,
                width: 850,
                minWidth: 850
            });

        return this._tilePanel;
    },

    getButtons: function(cfg) {
        if(!this._buttons)
        {
            this._buttons = [
                {
                    text: 'OK',
                    scope: this,
                    handler: function() {
                        core.invokeCallback(cfg.onOk, this.getInboxPanel().getSelectionModel().getSelected());
                        this.close();
                    }
                },
                {
                    text: 'Cancelar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ];
        }
        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Importar do Protocolo',
            modal: true,
            width: Ext.getBody().getBox().width * 0.9,
            height: Ext.getBody().getBox().height * 0.9,
            onOk: {fn: Ext.emptyFn},
        });

        var inboxPanel = this.getInboxPanel(cfg);
        inboxPanel.getTopToolbar().remove(0) //ações;
        inboxPanel.getTopToolbar().remove(0) //spacer;

        Ext.apply(cfg, {
            layout: 'border',
            border: false,
            buttons: this.getButtons(cfg),
            items: [
                inboxPanel,
                this.getTilePanel(cfg)
            ]
        });

        edocs.protocolo.SelectProtocolWindow.superclass.constructor.call(this, cfg);
    }
});
