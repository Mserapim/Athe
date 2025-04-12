Ext._define('planning.hiring.agreement.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getAgreementGrid: function () {
        if (!this._agreementGrid) {
            this._agreementGrid = Ext._create('planning.hiring.agreement.Grid', {
                minHeight: 100,
                region: 'center',
                baseParams: {
                    filter: Ext.encode([{
                        property: 'status__in',
                        value: [100, 1, 2, 3, 4, 5, 6],
                        stage: 1000
                    }])
                }
            });

            this._agreementGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function (selm) {
                    var selection = selm.getSelections();
                    if (selection.length > 0) {
                        this.contrato(selection[0].id);
                    } else {
                        this.contrato(null);
                    }
                }
            });

            this._agreementGrid.getStore().on({
                scope: this,
                load: function () {
                    this.observeContrato();
                }
            });
        }

        return this._agreementGrid;
    },

    getHistoryGrid: function () {
        if (!this._historyGrid)
            this._historyGrid = Ext._create('planning.hiring.agreementaction.Grid', {
                title: 'Histórico',
                gridAutoLoad: false,
            });

        return this._historyGrid;
    },

    getCommitmentNoteGrid: function () {
        if (!this._commitmentNoteGrid)
            this._commitmentNoteGrid = Ext._create('planning.hiring.commitmentnote.Grid', {
                title: 'Nota de Empenho',
                gridAutoLoad: false,
            });

        return this._commitmentNoteGrid;
    },

    getMeterageGrid: function () {
        if (!this._meterageGrid) {
            this._meterageGrid = Ext._create('planning.hiring.meterage.Grid', {
                title: 'Gestão de Pagamentos',
                gridAutoLoad: false,
            });

            this._meterageGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function (selm) {
                    var selection = selm.getSelections();
                    if (selection.length > 0) {
                        this._meterageGrid.pagamento = selection[0].id;
                        this._meterageGrid.contrato = selection[0].json.contrato;
                    } else {
                        this._meterageGrid.pagamento = null;
                    }
                }
            });
        }

        return this._meterageGrid;
    },

    getFeedbackDisplayTilePanel: function () {
        if (!this._feedbackDisplayTilePanel)
            this._feedbackDisplayTilePanel = Ext._create('core.TilePagePanel', {
                title: 'Resumo',
                region: 'east',
                height: '100%',
                width: '40%',
                split: true
            });

        return this._feedbackDisplayTilePanel;
    },

    getTabs: function () {
        if (!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                region: 'south',
                split: true,
                activeTab: 0,
                scope: this,
                height: 200,
                items: [
                    this.getHistoryGrid(),
                    this.getCommitmentNoteGrid(),
                    this.getMeterageGrid(),
                ]
            });

        return this._tabPanel;
    },

    contrato: function (value, observe) {
        observe = (observe === undefined ? true : observe);

        if (value !== undefined) {
            this._contrato = value;

            if (observe)
                this.observeContrato();
        }

        return this._contrato;
    },

    observeContrato: function () {
        var value = this.contrato();
        var selected = this.getAgreementGrid().getSelectionModel().getSelected();
        commitmentNoteGrid = this.getCommitmentNoteGrid();
        meterageGrid = this.getMeterageGrid();
        historyGrid = this.getHistoryGrid();
        tilePanel = this.getFeedbackDisplayTilePanel();

        if (value) {
            commitmentNoteGrid.enable();
            commitmentNoteGrid.setParam('contrato', value);
            commitmentNoteGrid.setFilterProperty('contrato', value, 10);

            meterageGrid.enable();
            meterageGrid.setParam('contrato', value);
            meterageGrid.setFilterProperty('contrato', value, 10);

            historyGrid.enable();
            historyGrid.setParam('contrato', value);
            historyGrid.setFilterProperty('contrato', value, 10);

            //Início do trecho referente ao tile
            var rest = this.getAgreementGrid().factoryRestful();
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
            //Fim do trecho dedicado ao tile

        } else {
            commitmentNoteGrid.setParam('contrato', 0);
            commitmentNoteGrid.setFilterProperty('contrato', value, 10, false);
            commitmentNoteGrid.getStore().removeAll();
            commitmentNoteGrid.disable();

            meterageGrid.setParam('contrato', 0);
            meterageGrid.setFilterProperty('contrato', value, 10, false);
            meterageGrid.getStore().removeAll();
            meterageGrid.disable();

            historyGrid.setParam('contrato', 0);
            historyGrid.setFilterProperty('contrato', value, 10, false);
            historyGrid.getStore().removeAll();
            historyGrid.disable();

            tilePanel.setPageContent('');
            tilePanel.disable();
        }
    },

    getGrouping: function () {
        if (!this._grouping)
            this._grouping = Ext._create('Ext.Panel', {
                region: 'center',
                layout: 'border',
                split: true,
                items: [
                    this.getAgreementGrid(),
                    this.getTabs()
                ],
            });

        return this._grouping;
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg, {
                title: 'Gestor de Contratos'
            }
        );

        Ext.apply(
            cfg, {
                layout: 'border',
                items: [
                    this.getGrouping(),
                    this.getFeedbackDisplayTilePanel(cfg),
                ]
            }
        );
        planning.hiring.agreement.Manage.superclass.constructor.call(this, cfg);
        this.observeContrato();
    }
});
