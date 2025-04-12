/**
 *
 **/
Ext._define('adm.contabilidade.NEManage', {
    extend: 'toolkit.widget.TabPanel',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Notas de Empenho'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: Ext._create('adm.contabilidade.NEGrid', {
                    region: 'center'
                })
            }
        );

        // this.callParent([cfg]);
        adm.contabilidade.NEManage.superclass.constructor.call(this, cfg);
    }
});
