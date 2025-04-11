
Ext._define('edocs.protocolo.ImpressoraManage', {
     extend: 'toolkit.widget.TabPanel',

     getGrid: function() {
         if(!this._grid)
             this._grid = Ext._create('edocs.protocolo.ImpressoraGrid', {
                region: 'center'
             });

         return this._grid;
     },

     constructor: function(cfg) {
         cfg = cfg ? cfg : {};

         Ext.applyIf(
             cfg,
             {
                title: 'Configurações de Impressoras'
             }
         );

         Ext.apply(
             cfg,
             {
                layout: 'border',
                items: this.getGrid()
             }
         );

         edocs.protocolo.ImpressoraManage.superclass.constructor.call(this, cfg);
     }
 });
