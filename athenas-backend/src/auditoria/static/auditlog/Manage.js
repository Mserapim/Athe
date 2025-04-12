/**
 *
 **/
 Ext._define('auditoria.auditlog.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGridPanel: function() {
        if(!this._gridPanel)
            this._gridPanel = Ext._create('auditoria.auditlog.Grid', {
                region: 'center',
                columnAction: false,
            });

        return this._gridPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Auditoria de Logs'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getGridPanel()
                ]
            }
        );

        // this.callParent([cfg]);
        auditoria.auditlog.Manage.superclass.constructor.call(this, cfg);
    }
});