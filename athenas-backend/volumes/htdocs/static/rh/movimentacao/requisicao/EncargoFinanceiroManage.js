/**
 *
 **/

Ext._define('rh.movimentacao.requisicao.EncargoFinanceiroManage', {
     extend: 'toolkit.widget.TabPanel',

     getGrid: function() {
         if(!this._grid)
             this._grid = Ext._create('rh.movimentacao.requisicao.EncargoFinanceiroGrid', {
                region: 'center'
             });

         return this._grid;
     },

     constructor: function(cfg) {
         cfg = cfg ? cfg : {};

         Ext.applyIf(
             cfg,
             {
                title: 'Gestor de Encargos Financeiros'
             }
         );

         Ext.apply(
             cfg,
             {
                layout: 'border',
                items: this.getGrid()
             }
         );

         rh.movimentacao.requisicao.EncargoFinanceiroManage.superclass.constructor.call(this, cfg);
     }
 });
