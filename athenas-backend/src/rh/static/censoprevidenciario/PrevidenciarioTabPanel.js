/**
 *
 **/
Ext._define('rh.pesquisa.PrevidenciarioTabPanel', {
    'extend': 'toolkit.widget.TabPanel',

    getPanel: function(){
        if (!this._panel){
            this._panel = Ext._create('rh.pesquisa.PrevidenciarioPanel', {
                region: 'center'
            })
        }
        return this._panel;
    },

    'constructor': function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                'title': 'Censo Previdenciário',
            }
        );


        Ext.apply(
            cfg,
            {
                items: this.getPanel(),
                layout: 'border',
                border: false
            }
        );

        // this.callParent([cfg]);
        rh.pesquisa.PrevidenciarioTabPanel.superclass.constructor.call(this, cfg);
    }
});