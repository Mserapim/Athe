/**
 *
 **/
Ext._define('apd.configuration.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getConfiguration: function() {
        if(!this.configuration) {
            this.configuration = Ext._create('apd.configuration.ConfigurationGrid', {
                region: 'center',
            });
        }

        return this.configuration;
    },
    
    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Configuração'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getConfiguration(),
                ]
            }
        );

        apd.configuration.Manage.superclass.constructor.call(this, cfg);
    }
});
