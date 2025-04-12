/**
 *
 **/
Ext._define('common.siatu.terceirizada.Manager', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._Grid){
            this._Grid = Ext._create('common.siatu.terceirizada.Grid', {
                region: 'center',
                // title:'Terceirizada',
            });
        }

         return this._Grid;
    },

    constructor: function(cfg) {        
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gerenciador de Terceirizadas'
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
        common.siatu.terceirizada.Manager.superclass.constructor.call(this, cfg);
    }
});
