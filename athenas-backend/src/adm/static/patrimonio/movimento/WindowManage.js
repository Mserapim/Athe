/**
 *
 **/
Ext._define('adm.patrimonio.movimento.WindowManage', {
    extend: 'Ext.Window',

    getPanelManage: function() {
        if(!this._panelManage)
            this._panelManage = Ext._create('adm.patrimonio.movimento.PanelManage', {
                region: 'center',
                border: false
            });

        return this._panelManage;
    },

    constructor: function(cfg) {
        var box = Ext.getBody().getBox();
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Movimentações',
                width: 0.95 * box.width,
                height: 0.85 * box.height
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [this.getPanelManage()]
            }
        );

        // this.callParent([cfg]);
        adm.patrimonio.movimento.WindowManage.superclass.constructor.call(this, cfg);
    }
});
