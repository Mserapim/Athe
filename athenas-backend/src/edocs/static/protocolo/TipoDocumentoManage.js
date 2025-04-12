
Ext._define('edocs.protocolo.TipoDocumentoManage', {
     extend: 'toolkit.widget.TabPanel',

     getGrid: function() {
         if(!this._grid)
             this._grid = Ext._create('edocs.protocolo.TipoDocumentoGrid', {
                region: 'center'
             });

         return this._grid;
     },

     constructor: function(cfg) {
         cfg = cfg ? cfg : {};

         Ext.applyIf(
             cfg,
             {
                title: 'Gestor de Tipos de Documentos'
             }
         );

         Ext.apply(
             cfg,
             {
                layout: 'border',
                items: this.getGrid()
             }
         );

         edocs.protocolo.TipoDocumentoManage.superclass.constructor.call(this, cfg);
     }
 });
