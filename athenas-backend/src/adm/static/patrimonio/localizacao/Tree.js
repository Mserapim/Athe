/**
 *
 **/
Ext._define('adm.patrimonio.localizacao.Tree', {
    extend: 'core.RestfulTree',

    restWindow: 'adm.patrimonio.localizacao.Window',

    folderIndexField: 'dentro_de',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {

            }
        );

        Ext.apply(
            cfg,
            {
            }
        );

        // this.callParent([cfg]);
        adm.patrimonio.localizacao.Tree.superclass.constructor.call(this, cfg);
    }
});
