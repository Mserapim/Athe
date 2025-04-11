/**
 *
 **/
Ext._define('common.siatu.configuration.distribuicao.Manager', {
    extend: 'toolkit.widget.TabPanel',

    getPanel: function(cfg) {
        if(!this._Panel)
            this._Panel = Ext._create('common.siatu.configuration.distribuicao.Panel', Ext.applyIf({
                frame: true,
            }, cfg));

        return this._Panel;
    },

    constructor: function(cfg) {        
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
                title: 'Distribuição automática',
                layout: 'fit',
                items: [
                    this.getPanel(cfg),

                ]
            }
        );

        common.siatu.configuration.distribuicao.Manager.superclass.constructor.call(this, cfg);
    }
});

