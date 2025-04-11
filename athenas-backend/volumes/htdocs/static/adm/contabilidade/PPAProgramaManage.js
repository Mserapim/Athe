/**
 *
 **/
Ext._define('adm.contabilidade.PPAProgramaManage', {
    extend: 'toolkit.widget.TabPanel',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Programa do PPA'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: Ext._create('adm.contabilidade.PPAProgramaGrid', {
                    region: 'center'
                })
            }
        );

        // this.callParent([cfg]);
        adm.contabilidade.PPAProgramaManage.superclass.constructor.call(this, cfg);
    }
});
