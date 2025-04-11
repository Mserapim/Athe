/**
 *
 **/

Ext._define('edocs.protocolo.channels.ChannelsManage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {

        if(!this._grid)
        {
            this._grid = Ext._create('edocs.protocolo.channels.ChannelsGrid', {
                region: 'center'
            });
        }

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Gestor de Canais de Protocolo',
            layout: 'border',
            items: [this.getGrid()]
        });

        edocs.protocolo.channels.ChannelsManage.superclass.constructor.call(this, cfg);
    }
});
