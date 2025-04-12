/**
 *
 **/
Ext._define('rh.pessoa.Manager', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._Grid){
            this._Grid = Ext._create('rh.pessoa.Grid', {
                region: 'center',
            });
        }

         return this._Grid;
    },

    constructor: function(cfg) {        
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gerenciador de Pessoas'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getGrid(),
                ]
            }
        );
        rh.pessoa.Manager.superclass.constructor.call(this, cfg);
    }
});
