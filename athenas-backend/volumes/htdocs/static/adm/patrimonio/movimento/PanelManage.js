/**
 *
 **/
Ext._define('adm.patrimonio.movimento.PanelManage', {
    extend: 'Ext.Panel',

    getMovimentoGrid: function() {
        if(!this._movimentoGrid) {
            this._movimentoGrid = Ext._create('adm.patrimonio.movimento.Grid', {
                region: 'center',
                bodyStyle: {
                    borderLeft: 'none',
                    borderRight: 'none'
                },
                toolbarStyle: {
                    borderTop: 'none',
                    borderLeft: 'none',
                    borderRight: 'none'
                },
                footerStyle: {
                    borderLeft: 'none',
                    borderRight: 'none'
                }
            });

            this._movimentoGrid.getSelectionModel().on({
                scope: this,
                rowselect: function(selectionModel, index, record) {
                    var selected = selectionModel.getSelected();
                    if (!selected) { return }

                    this.setMovimentoId(selected.get('pk'));
                    this.setOrigemId(selected.get('origem'));
                },
                rowdeselect: function(sm) {
                    this.setMovimentoId(null);
                },
            });

            this._movimentoGrid.getStore().on({
                scope: this,
                load: function() {
                    var selected = (this._movimentoGrid.getSelectionModel().getSelected());

                    if(selected)
                        this.setMovimentoId(selected.get('pk'));
                    else
                        this.setMovimentoId(null);
                }
            });
        }

        return this._movimentoGrid;
    },

    getMovimentoItemGrid: function() {
        if(!this._movimentoItemGrid){
            var self = this;
            this._movimentoItemGrid = Ext._create('adm.patrimonio.movimento.ItemGrid', {
                title: 'Itens na movimentação',
                flex: 1.0,
                border: false,
                gridAutoLoad: false,
                columAction: false,
                doubleClickHandler: function() {
                    self.getDetailMovimentItem();
                },
            });
        }
        return this._movimentoItemGrid;
    },

    getDetailMovimentItem: function(){
        selected = this.getMovimentoItemGrid().getSelectionModel().getSelections();
        if(selected.length > 0) {
            Ext._create('adm.patrimonio.movimento.DetailMovimentItemWindow', {
                pk: selected[0].get('pk')
            }).show();
        }
        else {
            Ext.Msg.show({
                title: 'Visualizando Item',
                msg: 'Primeiro selecione o item que deseja visualizar',
                icon : Ext.Msg.ERROR,
                buttons : Ext.Msg.OK,
            });
        }
    },

    doMove: function(tipo) {
        switch(tipo) {
            case 1:
                console.info('Retirar todos');
                break;
            case 2:
                console.info('Retirar selecionados');
                this.removeSelected();
                break;
            case 3:
                console.info('Adicionar selecionados');
                this.addSelected();
                break;
            case 4:
                console.info('Adicionar todos');
                break;

        }
    },

    removeSelected: function() {
        var rest = this.getMovimentoItemGrid().factoryRestful();
        var items = [];

        this.getMovimentoItemGrid().getSelectionModel().getSelections().map(
            function(record) {
                items.push(record.get('pk'));
            }
        );

        rest.remove(
            false, {
                params: {
                    filter: Ext.encode([
                        {
                            property: 'pk__in',
                            value: items
                        }
                    ])
                },
                externalCallback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getPatrimonioGrid().getStore().reload();
                            this.getMovimentoItemGrid().getStore().reload();
                        }
                    }
                }
            },
            {
                el: this.getEl()
            }
        );
    },

    addSelected: function() {
        var items = [];
        var rest = this.getMovimentoItemGrid().factoryRestful();
        var movimento = this.movimentoId;
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Processando...'});
        var store1 = this.getMovimentoItemGrid().getStore();
        var store2 = this.getPatrimonioGrid().getStore();

        mask.show();
        this.getPatrimonioGrid().getSelectionModel().getSelections().map(
            function(record) {
                rest.create(
                    {
                        params: {
                            movimento: movimento,
                            patrimonio: record.get('pk')
                        }
                    }
                );
            }
        );

        setTimeout(function() {
            mask.hide();
            store1.reload();
            store2.reload();
        }, 1000);
    },

    getControlPanel: function() {
        if(!this._controlPanel)
            this._controlPanel = Ext._create('Ext.Panel', {
                width: 40,
                frame: true,
                layout: 'vbox',
                bodyStyle: {
                    'border-top': 0,
                    'border-bottom': 0
                },
                items: [
                    {
                        xtype: 'panel',
                        flex: 1.0
                    },
                    {
                        xtype: 'button',
                        text: '<<',
                        width: 28,
                        height: 30,
                        style: {
                            padding: '2px 0 0 0'
                        },
                        scope: this,
                        handler: function() { this.doMove(1); }
                    },
                    {
                        xtype: 'button',
                        text: '<',
                        width: 28,
                        height: 30,
                        style: {
                            padding: '2px 0 0 0'
                        },
                        scope: this,
                        handler: function() { this.doMove(2); }
                    },
                    {
                        xtype: 'button',
                        text: '>',
                        width: 28,
                        height: 30,
                        style: {
                            padding: '2px 0 0 0'
                        },
                        scope: this,
                        handler: function() { this.doMove(3); }
                    },
                    {
                        xtype: 'button',
                        text: '>>',
                        width: 28,
                        height: 30,
                        style: {
                            padding: '2px 0 0 0'
                        },
                        scope: this,
                        handler: function() { this.doMove(4); }
                    },
                    {
                        xtype: 'panel',
                        flex: 1.0
                    }
                ]
            });

        return this._controlPanel;
    },

    getPatrimonioGrid: function() {
        if(!this._patrimonioGrid) {
            this._patrimonioGrid = Ext._create('adm.patrimonio.PatrimonioGrid', {
                title: 'Itens sob sua responsabilidade',
                flex: 1.0,
                border: false,
                configOrderToolBar: ['search', '->', 'download'],
                columAction: false
            });

            var fn = function(){};

            this.updateItem = fn;
            this.removeItems = fn;
            this.createItem = fn;

            // var tbar = this._patrimonioGrid.getToolbar();
            // tbar.remove(tbar.getComponent(0)); // Gerenciador
            // tbar.remove(tbar.getComponent(0)); // Separardor
            // tbar.remove(tbar.getComponent(0)); // Editar
            // tbar.remove(tbar.getComponent(0)); // Separardor

            var cm = this._patrimonioGrid.getColumnModel();
            cm.setHidden(5, true);
            cm.setHidden(6, true);
            cm.setHidden(7, true);
        }

        return this._patrimonioGrid;
    },

    setMovimentoId: function(movimentoId) {
        if (movimentoId !== this.movimentoId) {
            this.movimentoId = movimentoId;
            this._observeMovimentoId();
        }
    },

    setOrigemId: function(origemId) {
        if (origemId !== this.origemId) {
            this.origemId = origemId;
            this._observeOrigemId();
        }
    },

    _observeMovimentoId: function() {
        if (this.movimentoId) {
            this.getMovimentoItemGrid().enable();
            this.getMovimentoItemGrid().setFilterProperty('movimento', this.movimentoId);
        } else {
            this.getMovimentoItemGrid().getStore().removeAll();
            this.getMovimentoItemGrid().disable();
        }
    },

    _observeOrigemId: function() {
        if (this.origemId) {
            this.getPatrimonioGrid().setFilterProperty('localizacao__id', this.origemId);
        } else {
            this.getPatrimonioGrid().removeFilterProperty('localizacao__id');
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                border: false,
                items: [
                    this.getMovimentoGrid(),
                    {
                        listeners: {
                            scope: this,
                            render: function() {
                            }
                        },
                        region: 'south',
                        layout: 'hbox',
                        minHeight: 150,
                        height: 300,
                        split: true,
                        bodyStyle: {
                            'border-left': 0,
                            'border-right': 0
                        },
                        layoutConfig: {
                            align: 'stretch'
                        },
                        items: [
                            this.getPatrimonioGrid(),
                            this.getControlPanel(),
                            this.getMovimentoItemGrid()
                        ]
                    }
                ]
            }
        );

        // this.callParent([cfg]);
        adm.patrimonio.movimento.PanelManage.superclass.constructor.call(this, cfg);
        this._observeMovimentoId();
    }
});
