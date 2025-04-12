/**
 *
 **/
Ext._define('common.siatu.BaseConhecimento.objeto.Manager', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._Grid){
            this._Grid = Ext._create('common.siatu.BaseConhecimento.objeto.Grid', {
                region: 'center',
                minHeight: 200,
            });

            this._Grid.getSelectionModel().on({
                scope: this,
                rowselect: function(grid, index, record) {
                    this.getModeloGrid().setFilterProperty('objetos', record.get('pk'))
                }
            });
        }

         return this._Grid;
    },

    getModeloGrid: function() {
        if(!this._modeloGrid){
            this._modeloGrid = Ext._create('common.siatu.BaseConhecimento.modelo.Grid', {
                region: 'south',
                title: 'Modelos',
                split: true,
                height: 300,
                gridAutoLoad: false,
                minHeight: 200,
                hideItemsToolbar:['add', 'edit', 'search', 'remove']
            });
            var tbar = this._modeloGrid.getToolbar()
            tbar.hide()
        }

         return this._modeloGrid;
    },

    constructor: function(cfg) {        
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Objeto - Base de Conhecimento'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getGrid(),
                    this.getModeloGrid(),
                ]
            }
        );
        common.siatu.BaseConhecimento.objeto.Manager.superclass.constructor.call(this, cfg);
    }
});
