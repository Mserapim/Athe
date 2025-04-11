/**
 *
 **/

Ext._define('adm.patrimonio.parametro.ContaManage', {
     extend: 'toolkit.widget.TabPanel',

     getGrid: function() {
         if(!this._grid)
             this._grid = Ext._create('adm.patrimonio.parametro.ContaGrid', {
                region: 'center'
             });

         return this._grid;
     },

     constructor: function(cfg) {
         cfg = cfg ? cfg : {};

         Ext.applyIf(
             cfg,
             {
                title: 'Gestor de Contas Patrimoniais'
             }
         );

         Ext.apply(
             cfg,
             {
                layout: 'border',
                items: this.getGrid()
             }
         );

         adm.patrimonio.parametro.ContaManage.superclass.constructor.call(this, cfg);
     }
 });
