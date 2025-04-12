Ext._define('adm.patrimonio.Manage', {
    extend: 'toolkit.widget.TabPanel',

    _gridSelectionChangeEvent: function (selectionModel) {
        var selections = selectionModel.getSelections();

        if (selections.length > 0) {
            this.patrimony(selections[0].id);
        } else {
            this.patrimony(null);
        }
    },

    getIncorporacoesGrid: function () {
        if (!this._incorporacaoGrid) {
            this._incorporacaoGrid = Ext._create('adm.patrimonio.PatrimonioGrid', {
                region: 'west',
                border: false,
                split: true,
                columnAction: false,
            });

            this._incorporacaoGrid.on({
                scope: this,
                resize: function (grid, adjWidth) {
                    grid.getKeywordField().setWidth(adjWidth - 420);
                },
            });

            this._incorporacaoGrid.getSelectionModel().on({
                scope: this,
                selectionchange: this._gridSelectionChangeEvent,
            });

            this._incorporacaoGrid.getStore().on({
                scope: this,
                load: function () {
                    this.observePatrimony();
                }
            });
        }
        return this._incorporacaoGrid;
    },

    getFeedbackDisplayTilePanel: function () {
        if (!this._feedbackDisplayTilePanel)
            this._feedbackDisplayTilePanel = Ext._create('core.TilePagePanel', {
                title: 'Resumo',
                region: 'center',
            });

        return this._feedbackDisplayTilePanel;
    },

    patrimony: function (value, observe) {
        observe = (observe === undefined ? true : observe);

        if (value !== undefined) {
            this._patrimony = value;

            if (observe)
                this.observePatrimony();
        }
        return this._patrimony;
    },

    observePatrimony: function () {
        var value = this.patrimony();
        tilePanel = this.getFeedbackDisplayTilePanel();

        if (value) {
            // Início do trecho referente ao tile
            var rest = this.getIncorporacoesGrid().factoryRestful();
            var mask = new Ext.LoadMask(tilePanel.getEl(), { msg: 'buscando documento...' });
            mask.show();
            rest.rendererDocument(

                value, {
                    scope: this,
                    fn: function (document) {
                        tilePanel.enable();
                        tilePanel.setPageContent(document.content);
                    }
                }, {
                    fn: function (message) {
                        Ext.Msg.show({
                            title: 'Buscando documento',
                            msg: message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                }, {
                    fn: function () {
                        mask.hide();
                    }
                }
            );
        } else {
            tilePanel.setPageContent('');
            tilePanel.disable();
        }
    },

    _resizeEvent: function (panel, adjWidth) {
        toolkit.util.updateGridAndTileDimensions({
            target: this.getIncorporacoesGrid(),
            containerWidth: adjWidth,
        });
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Gestor Patrimonial',
        });

        Ext.apply(cfg, {
            layout: 'border',
            items: [
                this.getIncorporacoesGrid(),
                this.getFeedbackDisplayTilePanel(),
            ],
            listeners: {
                scope: this,
                resize: this._resizeEvent,
            },
        });

        adm.patrimonio.Manage.superclass.constructor.call(this, cfg);

        this.observePatrimony();
    }
});
