/**
 *
 **/
Ext._define('adm.patrimonio.avaliacao.Manage', {
    extend: 'toolkit.widget.TabPanel',

    avaliacao: function(value, observe) {
        observe = (observe === undefined ? true : observe);

        if (value !== undefined) {
            this._avaliacaoGrid = value;

            if (observe)
                this.observeAvaliacao();
        }

        return this._avaliacaoGrid;
    },

    observeAvaliacao: function() {
        var value = this.avaliacao();

        if (value) {
            this.getItemAvaliacaoGrid().enable();
            this.getItemAvaliacaoGrid().setParam('avaliacao', value.get('pk'));
            this.getItemAvaliacaoGrid().setFilterProperty('avaliacao', value.get('pk'), 100);
            this.getItemAvaliacaoGrid().setEvaluateType(value.get('tipo'));
        } else {
            this.getItemAvaliacaoGrid().disable();
            this.getItemAvaliacaoGrid().getStore().removeAll();
        }
    },

    getAvaliacaoGrid: function() {
        if(!this._avaliacaoGrid) {
            this._avaliacaoGrid = Ext._create('adm.patrimonio.avaliacao.Grid', {
                region: 'north',
                height: 250,
                split: true
            });

            this._avaliacaoGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(selm) {
                    var selection = selm.getSelections();

                    if(selection.length > 0)
                        this.avaliacao(selection[0]);
                    else
                        this.avaliacao(null);
                }
            });
        }

        return this._avaliacaoGrid;
    },

    getItemAvaliacaoGrid: function() {
        if(!this._itemAvaliacaoGrid)
            this._itemAvaliacaoGrid = Ext._create('adm.patrimonio.avaliacao.ItemGrid', {
                region: 'center',
                minHeight: 300,
                gridAutoLoad: false,
                title: 'Itens da Avaliação'
            });

        return this._itemAvaliacaoGrid;
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Avaliação de Bens'
        });

            Ext.apply(
                cfg,
                {
                    border: false,
                    layout: 'border',
                    items: [
                        this.getItemAvaliacaoGrid(),
                        this.getAvaliacaoGrid()
                    ]
                }
            );

        adm.patrimonio.avaliacao.Manage.superclass.constructor.call(this, cfg);
        this.avaliacao(cfg.oId === undefined ? null : cfg.oId);
    },
});
