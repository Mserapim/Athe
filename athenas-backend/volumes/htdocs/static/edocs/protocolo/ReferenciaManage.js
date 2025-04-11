
Ext._define('edocs.protocolo.ReferenciaManage', {
     extend: 'toolkit.widget.TabPanel',

     getGrid: function() {
         if(!this._grid)
             this._grid = Ext._create('edocs.protocolo.ReferenciaGrid', {
                region: 'center'
             });

         return this._grid;
     },

     constructor: function(cfg) {
         cfg = cfg ? cfg : {};

         Ext.applyIf(
             cfg,
             {
                title: 'Gestor de Referências'
             }
         );

         Ext.apply(
             cfg,
             {
                layout: 'border',
                items: this.getGrid()
             }
         );

         edocs.protocolo.ReferenciaManage.superclass.constructor.call(this, cfg);
     }
 });
