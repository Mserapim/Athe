/**
 *
 **/

Ext._define('rh.movimentacao.requisicao.Manage', {
     extend: 'toolkit.widget.TabPanel',

     getGrid: function() {
         if(!this._grid)
             this._grid = Ext._create('rh.movimentacao.requisicao.Grid', {
                region: 'center'
             });

         return this._grid;
     },

     constructor: function(cfg) {
         cfg = cfg ? cfg : {};

         Ext.applyIf(
             cfg,
             {
                title: 'Gestor de Movimentações de Requisição'
             }
         );

         Ext.apply(
             cfg,
             {
                layout: 'border',
                items: this.getGrid()
             }
         );

         rh.movimentacao.requisicao.Manage.superclass.constructor.call(this, cfg);
     }
 });
