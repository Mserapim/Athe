Ext._define('rh.replacement.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function(args) {
        if(!this._grid)
            this._grid = Ext._create('rh.replacement.Grid', {
                department: args.department,
                region: 'center'
            });

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Tabela - Substituições Automáticas'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid({department: cfg.department})
            }
        );

        rh.replacement.Manage.superclass.constructor.call(this, cfg);
    }
});
