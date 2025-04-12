/**
 *
 **/
Ext._define('adm.patrimonio.movimento.TabManage', {
    extend: 'toolkit.widget.TabPanel',

    getPanelManage: function() {
        if(!this._panelManage)
            this._panelManage = Ext._create('adm.patrimonio.movimento.PanelManage', {
                region: 'center',
                border: false
            });

        return this._panelManage;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Movimentações'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getPanelManage()
            }
        );

        // this.callParent([cfg]);
        adm.patrimonio.movimento.TabManage.superclass.constructor.call(this, cfg);
    }
});
