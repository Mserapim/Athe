/**
 *
 **/
Ext._define('adm.patrimonio.avaliacao.TabelaManage', {
    extend: 'toolkit.widget.TabPanel',

    observe: function() {
        if(this.getTabela()) {
            this.getItemPanel().enable();
            this.getParametroPanel().enable();

            this.getConservacaoGrid().setParam('tabela', this.getTabela());
            this.getConservacaoGrid().setFilterProperty('tabela', this.getTabela(), 100);

            this.getVidaUtilGrid().setParam('tabela', this.getTabela());
            this.getVidaUtilGrid().setFilterProperty('tabela', this.getTabela(), 100);

            this.getUtilizacaoGrid().setParam('tabela', this.getTabela());
            this.getUtilizacaoGrid().setFilterProperty('tabela', this.getTabela(), 100);
        }
        else {
            this.getItemPanel().disable();
            this.getParametroPanel().disable();
        }

        if(this.getTabela() && this.getGrupo()) {
            this.getItemTabelaGrid().enable();
            this.getItemTabelaGrid().setParam('tabela', this.getTabela());
            this.getItemTabelaGrid().setParam('grupo', this.getGrupo());

            this.getItemTabelaGrid().setFilterProperty('tabela', this.getTabela(), 100, false);
            this.getItemTabelaGrid().setFilterProperty('grupo', this.getGrupo(), 101, true);
        }
        else {
            this.getItemTabelaGrid().disable();
        }
    },

    setTabela: function(tabela) {
        this._tabelaId = tabela;
        this.observe();
    },

    setGrupo: function(grupo) {
        this._grupoId = grupo;
        this.observe();
    },

    getTabela: function() {
        return this._tabelaId;
    },

    getGrupo: function() {
        return this._grupoId;
    },

    getTabelaGrid: function() {
        if(!this._tabelaGrid) {
            this._tabelaGrid = Ext._create('adm.patrimonio.avaliacao.TabelaGrid', {
                title: 'Tabela',
                titleCollapsible: true,
                collapsible: true,
                region: 'north',
                minHeight: 195,
                height: 195,
                split: true
            });

            this._tabelaGrid.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, record) {
                    this.setTabela(record.get('pk'));
                }
            });
        }

        return this._tabelaGrid;
    },

    getItemTabelaGrid: function() {
        if(!this._itemTabelaGrid) {
            this._itemTabelaGrid = Ext._create('adm.patrimonio.avaliacao.ItemTabelaGrid', {
                title: 'Espécie',
                flex: 0.6,
                columnAction: false,
                gridAutoLoad: false,
                footerStyle: {
                    'border-bottom': 0,
                    'border-right': 0,
                },
                bodyStyle: {
                    'border-right': 0
                },
                toolbarStyle: {
                    'border-top': 0,
                    'border-right': 0
                }
            });

            var tbar = this._itemTabelaGrid.getToolbar();

            Ext.each(
                [2, 0],
                function(item) {
                    tbar.remove(item);
                }
            );

            this._itemTabelaGrid.getKeywordField().setWidth(175);
        }

        return this._itemTabelaGrid;
    },

    getGrupoGrid: function() {
        if(!this._grupoGrid) {
            this._grupoGrid = Ext._create('adm.patrimonio.parametro.GrupoEspecieGrid', {
                title: 'Grupo',
                flex: 0.4,
                gridAutoLoad: true,
                columnAction: false,
                style: {
                    'padding-right': '4px'
                },
                footerStyle: {
                    'border-bottom': 0,
                    'border-left': 0,
                },
                bodyStyle: {
                    'border-left': 0
                },
                toolbarStyle: {
                    'border-top': 0,
                    'border-left': 0
                }
            });

            this._grupoGrid.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, record) {
                    this.setGrupo(record.get('pk'));
                }
            });

            var tbar = this._grupoGrid.getToolbar();

            Ext.each(
                [3, 2, 1, 0],
                function(item) {
                    tbar.remove(item);
                }
            );

            this._grupoGrid.getKeywordField().setWidth(175);
        }

        return this._grupoGrid;
    },

    __prepereParametroGrid: function(grid) {
        var tbar = grid.getToolbar();

        tbar.remove(7);
        tbar.remove(6);
        tbar.remove(5);
        tbar.remove(4);
    },

    getConservacaoGrid: function() {
        if(!this._conservacaoGrid) {
            this._conservacaoGrid = Ext._create('adm.patrimonio.avaliacao.ParametroGrid', {
                title: 'Consevação',
                bodyStyle: {
                    'border-left': 0
                },
                headerStyle: {
                    'border-top': 0,
                    'border-left': 0
                },
                footerStyle: {
                    'border-bottom': 0,
                    'border-left': 0,
                },
                toolbarStyle: {
                    'border-left': 0,
                },
                columnAction: false
            });

            this._conservacaoGrid.restWindow = 'adm.patrimonio.avaliacao.ConservacaoWindow';
            this._conservacaoGrid.setParam('tipo', 1);
            this._conservacaoGrid.setFilterProperty('tipo', 1, 101);
            this._conservacaoGrid.setSortProperty('valor', 'DESC', 101);
            this.__prepereParametroGrid(this._conservacaoGrid);
        }

        return this._conservacaoGrid;
    },

    getUtilizacaoGrid: function() {
        if(!this._utilizacaoGrid) {
            this._utilizacaoGrid = Ext._create('adm.patrimonio.avaliacao.ParametroGrid', {
                title: 'Utilização',
                style: {
                    padding: '0 4px'
                },
                headerStyle: {
                    'border-top': 0,
                },
                footerStyle: {
                    'border-bottom': 0,
                },
                columnAction: false
            });

            this._utilizacaoGrid.restWindow = 'adm.patrimonio.avaliacao.UtilizacaoWindow';
            this._utilizacaoGrid.setParam('tipo', 2);
            this._utilizacaoGrid.setFilterProperty('tipo', 2, 101);
            this.__prepereParametroGrid(this._utilizacaoGrid);
        }

        return this._utilizacaoGrid;
    },

    getVidaUtilGrid: function() {
        if(!this._vidaUtilGrid) {
            this._vidaUtilGrid = Ext._create('adm.patrimonio.avaliacao.ParametroGrid', {
                title: 'Vida util',
                bodyStyle: {
                    'border-right': 0
                },
                headerStyle: {
                    'border-top': 0,
                    'border-right': 0
                },
                footerStyle: {
                    'border-bottom': 0,
                    'border-right': 0,
                },
                toolbarStyle: {
                    'border-right': 0,
                },
                columnAction: false
            });

            this._vidaUtilGrid.restWindow = 'adm.patrimonio.avaliacao.VidaUtilWindow';
            this._vidaUtilGrid.setParam('tipo', 3);
            this._vidaUtilGrid.setFilterProperty('tipo', 3, 101);
            this.__prepereParametroGrid(this._vidaUtilGrid);
        }

        return this._vidaUtilGrid;
    },

    getParametroPanel: function() {
        if(!this._parametroPanel)
            this._parametroPanel = Ext._create('Ext.Panel', {
                title: 'Parâmetros',
                layout: 'hbox',
                border: false,
                layoutConfig:  {
                    align: 'stretch'
                },
                defaults: {
                    flex: 1.0
                },
                items: [
                    this.getConservacaoGrid(),
                    this.getUtilizacaoGrid(),
                    this.getVidaUtilGrid()
                ]
            });

        return this._parametroPanel;
    },

    getItemPanel: function() {
        if(!this._itemPanel)
            this._itemPanel = Ext._create('Ext.Panel', {
                title: 'Itens',
                layout: 'hbox',
                layoutConfig:  {
                    align: 'stretch'
                },
                items: [
                    this.getGrupoGrid(),
                    this.getItemTabelaGrid()
                ]
            });

        return this._itemPanel;
    },

    getDetailPanel: function() {
        if(!this._detailPanel)
            this._detailPanel = Ext._create('Ext.TabPanel', {
                region: 'center',
                activeTab: 0,
                border: false,
                items: [
                    this.getItemPanel(),
                    this.getParametroPanel()
                ]
            });

        return this._detailPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Tabela de Avaliação'
            }
        );

        Ext.apply(
            cfg,
            {
                border: false,
                layout: 'border',
                items: [
                    this.getTabelaGrid(),
                    this.getDetailPanel()
                ]
            }
        );

        // this.callParent([cfg]);
        adm.patrimonio.avaliacao.TabelaManage.superclass.constructor.call(this, cfg);
        this.observe();
    }
});
