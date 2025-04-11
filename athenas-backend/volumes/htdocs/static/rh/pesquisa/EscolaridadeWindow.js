/**
 *
 **/
Ext._define('rh.pesquisa.EscolaridadeWindow', {
    'extend': 'Ext.Window',

    getPanel: function(){
        if (!this._panel){
            this._panel = Ext._create('rh.pesquisa.EscolaridadePanel', {
                region: 'center',
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
        var box = Ext.getBody().getBox();
        Ext.apply(
            cfg,
            {
                items: [
                    this.getPanel()
                ],
                layout: 'border',
                border: true,
                width: box.width*0.8,
                height: box.height*0.8,
                modal:true,
            }
        );
        // this.callParent([cfg]);
        rh.pesquisa.EscolaridadeWindow.superclass.constructor.call(this, cfg);
    }
});