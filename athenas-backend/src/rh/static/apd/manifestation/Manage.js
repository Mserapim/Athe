/**
 *
 **/
Ext._define('apd.manifestation.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getManifestation: function() {
        if(!this.manifestation) {
            this.manifestation = Ext._create('apd.manifestation.ManifestationGrid', {
                region: 'center',
            });
        }

        return this.manifestation;
    },
    
    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Manifestações'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getManifestation(),
                ]
            }
        );

        apd.manifestation.Manage.superclass.constructor.call(this, cfg);
    }
});
