/**
 *
 **/
Ext._define('auditoria.LineLogManage', {
    extend: 'toolkit.widget.TabPanel',

    getGridPanel: function() {
        if(!this._gridPanel)
            this._gridPanel = Ext._create('auditoria.LineLogGrid', {
                region: 'center'
            });

        return this._gridPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Visualizar Linhas de Auditoria'
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
        auditoria.LineLogManage.superclass.constructor.call(this, cfg);
    }
});
