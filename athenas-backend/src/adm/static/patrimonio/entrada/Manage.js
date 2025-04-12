/**
 *
 **/
Ext._define('adm.patrimonio.entrada.Manage', {
    extend: 'Ext.Window',

    getNotaGrid: function() {
        if(!this._notaGrid) {
            this._notaGrid = Ext._create('adm.patrimonio.entrada.Grid', {
                region: 'center',
                minHeight: 250
            });

            this._notaGrid.getSelectionModel().on({
                scope: this,
                rowselect: function(grid, index, record) {
                    this.setNota(record.get('pk'));
                }
            });

            this._notaGrid.getSelectionModel().on({
                scope: this,
                rowdeselect: function() {
                    this.setNota(undefined);
                }
            });

            this._notaGrid.getStore().on({
                scope: this,
                load: function() {
                    this.setNota(undefined);
                    this.getNotaGrid().getSelectionModel().clearSelections();
                }
            });
        }

        return this._notaGrid;
    },

    getItemGrid: function() {
        if(!this._itemGrid)
            this._itemGrid = Ext._create('adm.patrimonio.entrada.ItemEntradaGrid', {
                region: 'south',
                split: true,
                height: 300,
                minHeight: 250,
                gridAutoLoad: false
            });

        return this._itemGrid;
    },

     observe: function() {
        if(this.notaId) {
            this.getItemGrid().enable();
            this.getItemGrid().setFilterProperty('nota', this.notaId);
            this.getItemGrid().setParam('nota', this.notaId);
            this.getItemGrid().getStore().load({});
        }
        else {
            this.getItemGrid().disable();
            this.getItemGrid().getStore().removeAll();
        }
     },

     setNota: function(pk) {
        this.notaId = pk;
        this.observe();
     },

     getNota: function() {
        return this.notaId;
     },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gerenciador de Entrada'
            }
        );

        var box = Ext.getBody().getBox();

        Ext.apply(
            cfg,
            {
                width: 0.95 * box.width,
                height: 0.85 * box.height,
                resizable: false,
                layout: 'border',
                items: [
                    this.getNotaGrid(),
                    this.getItemGrid()
                ]
            }
        );

        // this.callParent([cfg]);
        adm.patrimonio.entrada.Manage.superclass.constructor.call(this, cfg);
        this.setNota(undefined);
    }
});
