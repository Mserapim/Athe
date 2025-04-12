
Ext._define('raf.solicitation.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getSolicitationGrid: function() {
        if(!this._solicitationGrid) {
            this._solicitationGrid = Ext._create('raf.solicitation.Grid', {
                region: 'center',
                title: 'Solicitações',
                disabled: false,
                gridAutoLoad: false,
                hideItemsToolbar: ['add','edit','remove'],
                columnAction: false,
            });
            this._solicitationGrid.setFilterProperty('status', 0, 100, true);
            
        }
        return this._solicitationGrid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Solicitações'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getSolicitationGrid(),
                ]
            }
        );

        raf.solicitation.Manage.superclass.constructor.call(this, cfg);

    }
});
