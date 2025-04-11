/**
 *
 **/
Ext._define('adm.patrimonio.localizacao.Manage', {
    extend: 'toolkit.widget.TabPanel',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Localizações'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    Ext._create('adm.patrimonio.localizacao.Tree', {
                        region: 'center',
                        rootVisible: false
                    })
                ]
            }
        );

        // this.callParent([cfg]);
        adm.patrimonio.localizacao.Manage.superclass.constructor.call(this, cfg);
    }
});
