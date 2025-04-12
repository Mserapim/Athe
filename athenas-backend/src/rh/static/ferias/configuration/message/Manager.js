/**
 *
 **/
if(typeof(rh.ferias) == 'undefined')
    Ext.ns("rh.ferias");

Ext._define('rh.ferias.configuration.message.Manager', {
    extend: 'toolkit.widget.TabPanel',

    getFormPanel: function(record) {
        if(!this._formPanel)
            this._formPanel = Ext._create('rh.ferias.configuration.message.Panel', {
                region: 'center',
                frame: true,
                values: record,
                oId: record.pk
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Configuração padrão de notificações'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getFormPanel(cfg.values)
                ]
            }
        );

        rh.ferias.configuration.message.Manager.superclass.constructor.call(this, cfg);
    }
});

