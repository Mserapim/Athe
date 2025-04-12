/**
 *
 **/
 Ext._define('auditoria.auditlog.ContentTypeManage', {
    extend: 'toolkit.widget.TabPanel',

    getGridPanel: function() {
        if(!this._gridPanel)
            this._gridPanel = Ext._create('auditoria.auditlog.ContentTypeGrid', {
                region: 'center'
            });

        return this._gridPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Modelos'
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
        auditoria.auditlog.ContentTypeManage.superclass.constructor.call(this, cfg);
    }
});