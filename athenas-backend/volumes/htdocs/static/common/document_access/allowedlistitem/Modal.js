Ext._define('common.document_access.allowedlistitem.Modal', {
    extend: 'Ext.Window',

    getGridPanel: function (cfg) {
        if (!this._gridPanel) {
            this._gridPanel = Ext._create('common.document_access.allowedlistitem.Grid', {
                region: 'center',
                gridAutoLoad: false,
                columnAction: false,
            });

            this._gridPanel.setParam('control', cfg.control);
            this._gridPanel.setFilterProperty('control', cfg.control, 1001);

        }

        return this._gridPanel;
    },

    getButtons: function (cfg) {
        if (!this._buttons) {
            this._buttons = [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            ];
        }

        return this._buttons;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Allowedlist',
            width: 1000,
            height: 400,
            modal: true,
        });

        Ext.apply(cfg, {
            layout: 'border',
            items: this.getGridPanel(cfg),
            buttons: this.getButtons(cfg),
        });

        common.document_access.log.Modal.superclass.constructor.call(this, cfg);
    }
});
