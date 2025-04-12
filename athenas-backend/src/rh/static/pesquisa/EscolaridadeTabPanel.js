/**
 *
 **/
Ext._define('rh.pesquisa.EscolaridadeTabPanel', {
    'extend': 'toolkit.widget.TabPanel',

    getPanel: function(){
        if (!this._panel){
            this._panel = Ext._create('rh.pesquisa.EscolaridadePanel', {
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
                'title': 'Pesquisa de Escolaridade',
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
        rh.pesquisa.EscolaridadeTabPanel.superclass.constructor.call(this, cfg);
    }
});