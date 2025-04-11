Ext._define('judicial.params.ActingZoneManage', {
    extend: 'toolkit.widget.TabPanel',

    getActingZoneGrid: function() {
        if(!this._characterGrid) {
            this._characterGrid = Ext._create('judicial.params.ActingZoneGrid', {
                region: 'center'
            });
        }

        return this._characterGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Área de Atuação'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                border: false,
                items: [
                    this.getActingZoneGrid()
                ]
            }
        );

        judicial.params.ActingZoneManage.superclass.constructor.call(this, cfg);
    }
});
