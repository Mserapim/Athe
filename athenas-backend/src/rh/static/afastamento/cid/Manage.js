/**
 *
 **/

 Ext._define('rh.afastamento.cid.Manage', {
	extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._grid){
            this._grid = Ext._create('rh.afastamento.cid.Grid', {
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
               title: 'CID - Classificação Internacional de Doenças'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.afastamento.cid.Manage.superclass.constructor.call(this, cfg);
    }
});
