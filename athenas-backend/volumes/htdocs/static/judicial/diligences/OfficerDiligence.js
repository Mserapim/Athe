/**
 *
 **/
 Ext._define('judicial.diligences.OfficerDiligence', {
    extend: 'toolkit.widget.TabPanel',

    getGridPanel: function(cfg) {
        if(!this._gridPanel)
            this._gridPanel = Ext._create('judicial.diligences.officer.DiligenceGrid', {
            });

        return this._gridPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestão de Oficiais'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'fit',
                items: [
                    this.getGridPanel(cfg)
                ]
            }
        );

        judicial.diligences.OfficerDiligence.superclass.constructor.call(this, cfg);
    }
});
