 Ext._define('rh.afastamento.cid.code.Manage', {
	extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._grid){
            this._grid = Ext._create('rh.afastamento.cid.code.Grid', {
                region: 'center',
                allowRemove: false
            });
        }
        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Códigos da CID-10'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.afastamento.cid.code.Manage.superclass.constructor.call(this, cfg);
    }
});
