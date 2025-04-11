Ext._define('adm.contabilidade.PPAManage', {
    extend: 'toolkit.widget.TabPanel',

    revision: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._revision = value;

            if(!prevent) this.observeRevision();
        }

        return this._revision;
    },

    observeRevision: function() {
        var value = this.revision();

        if(value) {
            this.getProgramGrid().enable();
            this.getProgramGrid().setParam('revisao', value);
            this.getProgramGrid().setFilterProperty('revisao', value, 100);
        }
        else {
            this.getProgramGrid().disable();
            this.getProgramGrid().setParam('revisao', 0);
            this.getProgramGrid().setFilterProperty('revisao', 0, 100, false);
            this.getProgramGrid().getStore().removeAll();
        }

        this.programa(null);
    },

    programa: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._programa = value;

            if(!prevent) this.observeProgram();
        }

        return this._programa;
    },/**
 *
 **/

    observeProgram: function() {
        var value = this.programa();

        if(value) {
            this.getPPAAcaoGrid().enable();
            this.getPPAAcaoGrid().setParam('programa', value);
            this.getPPAAcaoGrid().setFilterProperty('programa', value, 0);
        }
        else {
            this.getPPAAcaoGrid().disable();
            this.getPPAAcaoGrid().setParam('programa', 0);
            this.getPPAAcaoGrid().setFilterProperty('programa', 0, 0, false);
            this.getPPAAcaoGrid().getStore().removeAll();
        }

        this.acao(null);
    },

    getPPAAcaoGrid: function() {
        if(!this._ppaAcaoGrid) {
            this._ppaAcaoGrid = Ext._create('adm.contabilidade.PPAAcaoGrid', {
                gridAutoLoad: false,
                flex: 1,
                title: 'Ação'
            });

            this._ppaAcaoGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(selm) {
                    var data = selm.getSelected();

                    if(data)
                        this.acao(data.get('pk'));
                    else
                        this.acao(null);
                }
            });
        }

        return this._ppaAcaoGrid;
    },

    getProcessGrid: function() {
        if(!this._processGrid) {
            this._processGrid = Ext._create('adm.daily.financeiro.ProcessoPPAAcaoGrid', {
                gridAutoLoad: false,
                title: 'Processo'
            });

            this._processGrid.setFilterProperty('ano_referencia', new Date().getFullYear(), 10, false);
        }

        return this._processGrid;
    },

    getBudgetaryIndicatorGrid: function() {
        if (!this._budgetaryIndicatorGrid) {
            this._budgetaryIndicatorGrid = Ext._create('adm.contabilidade.budgetaryindicator.Grid', {
                gridAutoLoad: false,
                title: 'Indicador Orçamentário',
                columnAction: false,
                hideItemsToolbar: ['search'],
            });
        }

        return this._budgetaryIndicatorGrid;
    },

    acao: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._acao = value;

            if(!prevent) this.observeAcao();
        }

        return this._acao;
    },

    observeAcao: function() {
        var value = this.acao();

        if(value) {
            this.getProcessGrid().enable();
            this.getProcessGrid().setParam('ppa_acao', value);
            this.getProcessGrid().setFilterProperty('ppa_acao', value, 1000);

            this.getBudgetaryIndicatorGrid().enable();
            this.getBudgetaryIndicatorGrid().setParam('action', value);
            this.getBudgetaryIndicatorGrid().setFilterProperty('action', value, 1001);
        }
        else {
            this.getProcessGrid().disable();
            this.getProcessGrid().setParam('ppa_acao', 0);
            this.getProcessGrid().setFilterProperty('ppa_acao', 0, 1000, false);
            this.getProcessGrid().getStore().removeAll();

            this.getBudgetaryIndicatorGrid().disable();
            this.getBudgetaryIndicatorGrid().setParam('action', 0);
            this.getBudgetaryIndicatorGrid().setFilterProperty('action', 0, 1001, false);
            this.getBudgetaryIndicatorGrid().getStore().removeAll();
        }
    },

    getDetailPanel: function() {
        if(!this._detailPanel)
            this._detailPanel = Ext._create('Ext.Panel', {
                layout: {
                    type: 'vbox',
                    align: 'stretch'
                },
                region: 'center',
                border: false,
                items: [
                    this.getPPAAcaoGrid(),
                    new Ext.TabPanel({
                        flex: 1,
                        activeTab: 0,
                        items: [
                            this.getProcessGrid(),
                            this.getBudgetaryIndicatorGrid()
                        ]
                    }),
                ]
            });

        return this._detailPanel;
    },

    getRevisionGrid: function() {
        if(!this._revisionGrid) {
            this._revisionGrid = Ext._create('adm.contabilidade.PPARevisaoGrid', {
                region: 'north',
                split: true,
                minHeight: 150,
                flex: 1,
                title: 'Revisão',
                hideColumns: ['unicode', 'publicacao_unicode'],
                columnAction: false,
                configOrderToolBar: ['add', 'edit', 'remove', '->'],
            });

            this._revisionGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(selm) {
                    var data = selm.getSelected();

                    if(data)
                        this.revision(data.get('pk'));
                    else
                        this.revision(null);
                }
            });

            this._revisionGrid._toolbar.items.each(
               function(btn) {
                  if(btn.text != 'Filtro')
                      btn.text = '';
               }
            );

            this._revisionGrid.setFilterProperty('ativo', true, 10, false);
        }

        return this._revisionGrid;
    },

    getProgramGrid: function() {
        if(!this._programaGrid) {
            this._programaGrid = Ext._create('adm.contabilidade.PPAProgramaGrid', {
                    region: 'center',
                    gridAutoLoad: false,
                    title: 'Programa',
                    flex: 1,
                    hideColumns: ['revisao_unicode'],
                    columnAction: false,
                    configOrderToolBar: ['add', 'edit', 'remove'],
                }
            );

            this._programaGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(selm) {
                    var data = selm.getSelected();

                    if(data)
                        this.programa(data.get('pk'));
                    else
                        this.programa(null);
                }
            });

            this._programaGrid._toolbar.items.each(
               function(btn) {
                   btn.text = '';
               }
            );
        }

        return this._programaGrid;
    },

    getControlPanel: function() {
        if(!this._controlPanel)
            this._controlPanel = Ext._create('Ext.Panel', {
                layout: {
                    type: 'vbox',
                    align: 'stretch'
                },
                region: 'west',
                minWidth: 300,
                width: 380,
                split: true,
                border: false,
                items: [
                    this.getRevisionGrid(),
                    this.getProgramGrid()
                ]
            });

        return this._controlPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor do PPA'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getDetailPanel(),
                    this.getControlPanel()
                ]
            }
        );

        adm.contabilidade.PPAManage.superclass.constructor.call(this, cfg);
        this.observeRevision();
    }
});
