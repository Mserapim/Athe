/**
 *
 **/
Ext._define('cif.referenceperiod.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getReferencePeriod: function() {
        if(!this.reference) {
            this.reference = Ext._create('cif.referenceperiod.ReferencePeriodGrid', {
                region: 'center',
            });
        }

        return this.reference;
    },
    
    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Períodos de Referência'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getReferencePeriod(),
                ]
            }
        );

        cif.referenceperiod.Manage.superclass.constructor.call(this, cfg);
    }
});
