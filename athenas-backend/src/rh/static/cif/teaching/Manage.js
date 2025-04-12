/**
 *
 **/
Ext._define('cif.teaching.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getTeaching: function() {
        if(!this.teaching) {
            this.teaching = Ext._create('cif.teaching.TeachingGrid', {
                region: 'center',
            });
        }

        return this.teaching;
    },
    
    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Docência'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getTeaching(),
                ]
            }
        );

        cif.teaching.Manage.superclass.constructor.call(this, cfg);
    }
});
