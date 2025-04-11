/**
 *
 **/
Ext._define('cif.codeproperty.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getCodeProperty: function() {
        if(!this.codeproperty) {
            this.codeproperty = Ext._create('cif.codeproperty.CodePropertyGrid', {
                region: 'center',
            });
        }

        return this.codeproperty;
    },
    
    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Códigos de Bens'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getCodeProperty(),
                ]
            }
        );

        cif.codeproperty.Manage.superclass.constructor.call(this, cfg);
    }
});
