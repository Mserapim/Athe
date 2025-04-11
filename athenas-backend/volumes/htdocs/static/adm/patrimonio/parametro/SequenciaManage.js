/**
 *
 **/

Ext._define('adm.patrimonio.parametro.SequenciaManage', {
     extend: 'toolkit.widget.TabPanel',

     getGrid: function() {
         if(!this._grid)
             this._grid = Ext._create('adm.patrimonio.parametro.SequenciaGrid', {
                region: 'center'
             });

         return this._grid;
     },

     constructor: function(cfg) {
         cfg = cfg ? cfg : {};

         Ext.applyIf(
             cfg,
             {
                title: 'Gestor de Sequencias Patrimoniais'
             }
         );

         Ext.apply(
             cfg,
             {
                layout: 'border',
                items: this.getGrid()
             }
         );

         adm.patrimonio.parametro.SequenciaManage.superclass.constructor.call(this, cfg);
     }
 });
