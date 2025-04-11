/**
 *
 **/
Ext._define('judicial.outcourtlawsuit.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getOutcourtLawsuitGrid: function() {
        if(!this._outcourtlawsuit) {
            this._outcourtlawsuit = Ext._create('judicial.outcourtlawsuit.OutCourtLawsuitAdminGrid', {
                region: 'center',
                gridAutoLoad: false
            });

            this._outcourtlawsuit.setFilterProperty('attached_lawsuit', null, 100002, false);
            this._outcourtlawsuit.setFilterProperty('removed_by', null, 3000, false);
            this._outcourtlawsuit.setFilterProperty('closed_by', null, 3002);
        }

        return this._outcourtlawsuit;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Procedimentos'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getOutcourtLawsuitGrid(),
                ]
            }
        );

        judicial.outcourtlawsuit.Manage.superclass.constructor.call(this, cfg);
    }
});
