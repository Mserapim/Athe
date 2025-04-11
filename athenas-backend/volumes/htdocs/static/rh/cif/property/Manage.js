/**
 *
 **/
Ext._define('cif.property.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getProperty: function() {
        if(!this.property) {
            this.property = Ext._create('cif.property.PropertyGrid', {
                region: 'center',
            });
        }

        return this.property;
    },
    
    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Bens e Valores'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getProperty(),
                ]
            }
        );

        cif.property.Manage.superclass.constructor.call(this, cfg);
    }
});
