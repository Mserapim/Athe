
Ext._define('judicial.bloke.BlokeAddressPanel', {
    extend: 'Ext.Panel',

    getBlokeAddressPanel: function(cfg) {
        if(!this._blokeAddressPanel)
            this._blokeAddressPanel = Ext._create('judicial.bloke.BlokeAddressGrid', {
                gridAutoLoad: ((cfg || {}).gridAutoLoad || true),
                region: 'north',
                minHeight: 150,
                height: 150,
                split: true
            });

        return this._blokeAddressPanel;
    },

    getDisplayAddressPanel: function(cfg) {
        if(!this.displayAddressPanel)
            this.displayAddressPanel = Ext._create('core.TilePagePanel', {
                region: 'center',
                minHeight: 150,
                papperModel: 'card'
            });

        return this.displayAddressPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Endereço'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                border: false,
                minHeight: 320,
                items: [
                    this.getBlokeAddressPanel(cfg),
                    this.getDisplayAddressPanel(cfg)
                ]
            }
        );

        judicial.bloke.BlokeAddressPanel.superclass.constructor.call(this, cfg);
    }
});
