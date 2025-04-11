/**
 *
 **/
Ext._define('common.siatu.servico.ManagerGerente', {
    extend: 'toolkit.widget.TabPanel',

    getListaAtendenteGrid: function() {
        if(!this._listaAtendenteGrid){
             this._listaAtendenteGrid = Ext._create('common.siatu.servico.AtendentesGrid', {
                flex: 1.0,
                border: false,
                gridAutoLoad: false,
                title:'Atendentes do serviço',
                columnAction:false,
                doubleClickHandler: this.mudaDistAutomatica
            });

            var tbar = this._listaAtendenteGrid.getToolbar()
            tbar.add([
                {
                    text: 'Distribuição Automática/Manual',
                    iconCls: 'icon-siatu icon-siatu-reincidencia',
                    scope: this,
                    handler: function() {this.mudaDistAutomatica(this._listaAtendenteGrid, true)}
                }
            ])
         }

         return this._listaAtendenteGrid;
    },

    mudaDistAutomatica: function(grid, button) {
        var selected = grid.getSelectionModel().getSelected()
        if (selected){
            var rest = grid.factoryRestful();
            rest.update(
                selected.get('pk'),{
                    params: {
                        servico: grid.getParams().servico,
                        distribuicao_automatica: !selected.get('distribuicao_automatica'),
                    },
                    externalCallback: {
                        success: {
                            fn: function() {
                                grid.getStore().reload()
                            }
                        }
                    }
                }
            );
        }
        else if (button)
            Ext.Msg.show({
                title: 'Distribuição Automática',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item.'
            });

    },

    getAtendenteGrid: function() {
        if(!this._atendenteGrid) {
            this._atendenteGrid = Ext._create('common.siatu.atendente.Grid', {
                title: 'Todos atendentes cadastrados',
                flex: 1.0,
                border: false,
                columnAction:false,
            });

            var tbar = this._atendenteGrid.getToolbar()
            tbar.remove(tbar.getComponent(1)); // Remover
        }

        return this._atendenteGrid;
    },

    setStoreAtendenteGrid: function() {
        var grid = this.getAtendenteGrid()
        grid.setFilterProperty('servicos_vinculados', this.ServicoId, -1001);

        // rest = Ext._create('common.siatu.atendente.Restful',{});
        // store = Ext._create('Ext.data.Store', {
        //             proxy: Ext._create('Ext.data.HttpProxy', {
        //                 api: {
        //                     read: core.callAction("SiatuAtendente", "action_atendentes_not_in_service",this.ServicoId)
        //                 },
        //                 disableCaching: rest.disableCaching,
        //                 defaultHeaders: rest.defaultHeaders,
        //             }),
        //             reader: Ext._create('Ext.data.JsonReader', {
        //                 idProperty: 'pk',
        //                 root: 'collection',
        //                 totalProperty: 'count',
        //                 successProperty: 'success',
        //                 messageProperty: 'message',
        //                 fields: rest.getFields()
        //             }),
        //             autoLoad: true
        //         })
        // this.getAtendenteGrid().setStore(store)
        // this.getAtendenteGrid().reconfigure(
        //     store,
        //     this.getAtendenteGrid().getColumnModel()
        // )
    },

    getControlPanelAtendente: function() {
        if(!this._controlPanelAtendente)
            this._controlPanelAtendente = Ext._create('Ext.Panel', {
                width: 40,
                frame: true,
                layout: 'hbox',
                bodyStyle: {
                    'border-left': 0,
                    'border-right': 0
                },
                items: [
                    {
                        xtype: 'panel',
                        flex: 1.0
                    },
                    {
                        xtype: 'button',
                        text: 'Adicionar',
                        iconCls: 'icon-siatu icon-siatu-move-down',
                        width: 28,
                        height: 30,
                        style: {
                            padding: '2px 0 0 0'
                        },
                        scope: this,
                        handler: function() {  this.addSelectedAtendente() }
                    },
                    {
                        xtype: 'panel',
                        width:60,
                    },
                    {
                        xtype: 'button',
                        text: 'Remover',
                        iconCls: 'icon-siatu icon-siatu-move-up',
                        width: 28,
                        height: 30,
                        style: {
                            padding: '2px 0 0 0'
                        },
                        scope: this,
                        handler: function() { this.removeSelectedAtendente()}
                    },
                    {
                        xtype: 'panel',
                        flex: 1.0
                    }
                ]
            });

        return this._controlPanelAtendente;
    },

    updateAtendentes: function(items){
        var servico = this.ServicoId;
        var rest = this.getServicoTree().factoryRestful();
        rest.update(
            servico,{
                params: {
                    lista_atendentes: items,
                },
                externalCallback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.setStoreAtendenteGrid()
                            this.getListaAtendenteGrid().getStore().load()
                        }
                    }
                }
            },
            {
                el: this.getEl()
            }
        );
    },

    addSelectedAtendente: function() {
        if(this.getServico()==undefined){
            console.debug('Botão adicionar atendente de serviço, não há serviço selecionado')
            return '';
        }
        var items = [];
        var rest = this.getListaAtendenteGrid().factoryRestful();
        var servico = this.ServicoId;
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Processando...'});
        var store1 = this.getListaAtendenteGrid().getStore();
        var store2 = this.getAtendenteGrid().getStore();
        var selections = this.getAtendenteGrid().getSelectionModel().getSelections();

        if(selections.length==0){
            console.debug('Não há atendente selecionado para adicionar ao serviço')
            return '';
        }
        mask.show()

        selections.map(
            function(record) {
                rest.create(
                    {
                        params: {
                            servico: servico,
                            atendente: record.get('pk')
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

    removeSelectedAtendente: function() {
        if(this.getServico()==undefined){
            console.debug('Botão excluir atendente de serviço, não há serviço selecionado')
            return '';
        }
        var rest = this.getListaAtendenteGrid().factoryRestful();
        var items = [];
        var selections = this.getListaAtendenteGrid().getSelectionModel().getSelections();

        if(selections.length==0){
            console.debug('Não há atendente selecionado para remover do serviço')
            return '';
        }

        selections.map(
            function(record) {
                items.push(record.get('pk'))
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
                            this.getAtendenteGrid().getStore().reload();
                            this.getListaAtendenteGrid().getStore().reload();
                        }
                    }
                }
            },
            {
                el: this.getEl()
            }
        );
    },

    observeServico: function() {
        if(this.ServicoId) {
            this.getTabPanel().enable();
            this.getListaAtendenteGrid().setTitle("Atendentes do serviço "+this.getServicoUnicode())
            this.getListaAtendenteGrid().setFilterProperty('servico', this.getServico());
            this.setStoreAtendenteGrid()
        }
        else {
            this.getListaAtendenteGrid().disable();
        }
    },

    setServico: function(pk, text) {
        this.ServicoId = pk;
        this.ServicoUnicode = text;
    },

    getServico: function() {
        return this.ServicoId;
    },

    getServicoUnicode: function() {
        return this.ServicoUnicode;
    },

    getServicoTree: function() {
        if(!this._servicoTree){
            this._servicoTree = Ext._create('common.siatu.servico.Tree', {
                autoScroll: true,
                flex: 0.4,
                rootVisible: false,
            })

            // Filtra servicos do gerente
            // this._servicoTree.getLoader().baseParams = {filter: Ext.encode([{"property":"pk__in","value":this.lista_servicos,"stage":0}])}

            tbar = this._servicoTree.getToolbar()
            tbar.remove(tbar.getComponent(0))//Adicionar
            tbar.remove(tbar.getComponent(0))//Editar
            tbar.remove(tbar.getComponent(0))//Remover
            tbar.remove(tbar.getComponent(0))//Separador
            tbar.remove(tbar.getComponent(0))//Mover
            tbar.remove(tbar.getComponent(0))//Separador

            this._servicoTree.getSelectionModel().on({
                scope: this,
                selectionchange: function(selModel, Node) {
                    if (Node){
                        this.setServico(Node.id, Node.text);
                        this.getListaAtendenteGrid().setParam('servico', this.getServico())
                        this.observeServico();
                    }
                },
            });

            this._servicoTree.on({
                scope: this,
                load: function(node) {
                    Ext.each(
                        node.childNodes,
                        function(childNode) {
                            if(this.lista_servicos.indexOf(parseInt(childNode.id)) == -1){
                                childNode.disable();
                            }
                        },
                        this
                    );
                },
            })
        }

        return this._servicoTree;
    },

    getTabPanel: function() {
        if(!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                border: false,
                activeTab: 0,
                flex: 0.6,
                disabled: true,
                items: [
                    {
                            title: 'Atendentes',
                            layout: 'vbox',
                            split:true,
                            bodyStyle: {
                            'border-top': 0,
                            'border-bottom': 0
                            },
                            layoutConfig: {
                            align: 'stretch',
                            },
                            items:[
                                this.getAtendenteGrid(),
                                this.getControlPanelAtendente(),
                                this.getListaAtendenteGrid(),
                            ]
                    },
                ]
            });

        return this._tabPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        this.lista_servicos = cfg.lista_servicos

        Ext.applyIf(
            cfg,
            {
                title: 'Gerenciador de Serviços'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'hbox',
                layoutConfig: {
                    align: 'stretch',
                },
                items: [
                        this.getServicoTree(),
                        this.getTabPanel(),
                    ]

            }


        );

        common.siatu.servico.ManagerGerente.superclass.constructor.call(this, cfg);
    }
});

