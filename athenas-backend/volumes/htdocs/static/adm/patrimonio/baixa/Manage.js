Ext._define('adm.patrimonio.baixa.Manage', {
    extend: 'Ext.Window',

    getNotaGrid: function () {
        if (!this._notaGrid) {
            this._notaGrid = Ext._create('adm.patrimonio.baixa.Grid', {
                region: 'north',
                minHeight: 250,
                height: 250
            });

            this._notaGrid.getSelectionModel().on({
                scope: this,
                rowselect: function (grid, index, record) {
                    this.setNota(record.get('pk'), false);
                    this.setConta(record.get('conta'), true);
                }
            });

            this._notaGrid.getSelectionModel().on({
                scope: this,
                rowdeselect: function () {
                    this.setNota(undefined, false);
                    this.setConta(undefined, true);
                }
            });

            this._notaGrid.getStore().on({
                scope: this,
                load: function () {
                    this.setNota(undefined);
                    this.setConta(undefined, true);
                    this.getNotaGrid().getSelectionModel().clearSelections();
                }
            });
        }

        return this._notaGrid;
    },

    getItemGrid: function () {
        if (!this._itemGrid)
            this._itemGrid = Ext._create('adm.patrimonio.baixa.ItembaixaGrid', {
                region: 'center',
                split: true,
                minHeight: 250,
                gridAutoLoad: false
            });

        return this._itemGrid;
    },

    observe: function () {
        if (this.notaId) {
            this.getItemGrid().enable();
            this.getItemGrid().setFilterProperty('nota', this.notaId);
            this.getItemGrid().setParam('nota', this.notaId);
            this.getItemGrid().setParam('conta', this.contaId);
            this.getItemGrid().getStore().load({});
        }
        else {
            this.getItemGrid().disable();
            this.getItemGrid().getStore().removeAll();
        }
    },

    setNota: function (pk, dispatch) {
        this.notaId = pk;
        if (dispatch) this.observe();
    },

    getNota: function () {
        return this.notaId;
    },

    setConta: function (pk, dispatch) {
        this.contaId = pk;
        if (dispatch) this.observe();
    },

    getConta: function () {
        return this.contaId;
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gerenciador de baixa'
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
        adm.patrimonio.baixa.Manage.superclass.constructor.call(this, cfg);
        this.setNota(undefined);
    }
});
