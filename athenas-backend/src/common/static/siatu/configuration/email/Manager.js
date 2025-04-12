/**
 *
 **/
Ext._define('common.siatu.configuration.email.Manager', {
    extend: 'toolkit.widget.TabPanel',

    getFormPanel: function(record) {
        if(!this._formPanel)
            this._formPanel = Ext._create('common.siatu.configuration.email.Panel', {
                region: 'center',
                frame: true,
                values: record,
                oId: record.pk,
            });

        return this._formPanel;
    },

    constructor: function(cfg) {        
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Configuração padrão de emails',
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getFormPanel(cfg.values),

                ]
            }
        );

        common.siatu.configuration.email.Manager.superclass.constructor.call(this, cfg);
    }
});

