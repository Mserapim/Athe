/**
 *
 **/

Ext._define('rh.movimentacao.possession.request.PeriodoRequisicaoManage', {
     extend: 'toolkit.widget.TabPanel',

     getGrid: function() {
         if(!this._grid)
             this._grid = Ext._create('rh.movimentacao.possession.request.PeriodoRequisicaoGrid', {
                region: 'center'
             });

         return this._grid;
     },

     constructor: function(cfg) {
         cfg = cfg ? cfg : {};

         Ext.applyIf(
             cfg,
             {
                title: 'Gestor de Períodos de Requisições'
             }
         );

         Ext.apply(
             cfg,
             {
                layout: 'border',
                items: this.getGrid()
             }
         );

         rh.movimentacao.possession.request.PeriodoRequisicaoManage.superclass.constructor.call(this, cfg);
     }
 });
