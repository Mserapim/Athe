Ext._define('web.cms.metadata.MetaKeyManager', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function()
    {
        if(!this._grid)
            this._grid = Ext._create('web.cms.metadata.MetaKeyGrid', {
                region: 'center'
            });

        return this._grid;
    },

    constructor: function(cfg)
    {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Gestor de Nomes de Metadados',
            layout: 'border',
            items: [this.getGrid()]
        });

        web.cms.metadata.MetaKeyManager.superclass.constructor.call(this, cfg);
    }
});