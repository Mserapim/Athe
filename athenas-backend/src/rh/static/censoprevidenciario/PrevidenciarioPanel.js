/**
 *
 **/
Ext._define('rh.pesquisa.PrevidenciarioPanel', {
    'extend': 'Ext.Panel',

    getGridPanel: function(){
        if (!this._gridPanel){
            this._gridPanel = Ext._create('rh.pesquisa.PrevidenciarioRestfulGrid', {
                region: 'center',
                border: false,
            })
        }
        return this._gridPanel;
    },

    'constructor': function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                // 'title': 'Undefined',
            }
        );


        Ext.apply(
            cfg,
            {
                items: [
                    this.getGridPanel()
                ],
                layout:'border',
                border: false
            }
        );

        // this.callParent([cfg]);
        rh.pesquisa.PrevidenciarioPanel.superclass.constructor.call(this, cfg);
    }
});