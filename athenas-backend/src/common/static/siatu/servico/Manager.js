/**
 *
 **/
Ext._define('common.siatu.servico.Manager', {
    extend: 'toolkit.widget.TabPanel',

    getListaAtendenteGrid: function() {
        if(!this._listaAtendenteGrid){
             this._listaAtendenteGrid = Ext._create('common.siatu.servico.AtendentesGrid', {
                flex: 1.0,
                border: false,
                gridAutoLoad: false,
                title:'Atendentes do serviço',
                columnAction:false,
            });
         }

         return this._listaAtendenteGrid;
    },

    getAtendenteGrid: function() {
        if(!this._atendenteGrid) {
            this._atendenteGrid = Ext._create('common.siatu.atendente.Grid', {
                flex: 1.0,
                border: false,
                columnAction:false,
            });

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
        // })
        // this.getAtendenteGrid().setStore(store)
        // this.getAtendenteGrid().reconfigure(
        //     store,
        //     this.getAtendenteGrid().getColumnModel()
        // )
    },

    getListaGerenteGrid: function() {
        if(!this._listaGerenteGrid){
            this._listaGerenteGrid = Ext._create('common.siatu.gerente.Grid', {
                flex: 1.0,
                border: false,
                gridAutoLoad: false,
                title:'Gerentes do serviço',
                columnAction:false,
            });

            var tbar = this._listaGerenteGrid.getToolbar()
            tbar.remove(tbar.getComponent(0)); // Adicionar
            tbar.remove(tbar.getComponent(0)); // Remover
            tbar.remove(tbar.getComponent(0)); // Separador
        }

         return this._listaGerenteGrid;
     },

    getGerenteGrid: function() {
        if(!this._gerenteGrid) {
            this._gerenteGrid = Ext._create('common.siatu.gerente.Grid', {
                // title: 'Gerentes',
                flex: 1.0,
                border: false,
                columnAction:false,
            });
        }

        return this._gerenteGrid;
    },

    setStoreGerenteGrid: function() {
        rest = Ext._create('common.siatu.gerente.Restful',{});
        store = Ext._create('Ext.data.Store', {
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        api: {
                            read: core.callAction("SiatuGerente", "action_gerentes_not_in_service",this.ServicoId)
                        },
                        disableCaching: rest.disableCaching,
                        defaultHeaders: rest.defaultHeaders,
                    }),
                    reader: Ext._create('Ext.data.JsonReader', {
                        idProperty: 'pk',
                        root: 'collection',
                        totalProperty: 'count',
                        successProperty: 'success',
                        messageProperty: 'message',
                        fields: rest.getFields()
                    }),
                    autoLoad: true
        })
        this.getGerenteGrid().setStore(store)
        this.getGerenteGrid().reconfigure(
            store,
            this.getGerenteGrid().getColumnModel()
        )
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

    getControlPanelGerente: function() {
        if(!this._controlPanelGerente)
            this._controlPanelGerente = Ext._create('Ext.Panel', {
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
                        handler: function() {  this.addSelectedGerente() }
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
                        handler: function() { this.removeSelectedGerente()}
                    },
                    {
                        xtype: 'panel',
                        flex: 1.0
                    }
                ]
            });

        return this._controlPanelGerente;
    },

    updateGerentes: function(items){
        var servico = this.ServicoId;
        var rest = this.getServicoTree().factoryRestful();
        rest.update(
            servico,{
                params: {
                    lista_gerentes: items,
                },
                externalCallback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.setStoreGerenteGrid()
                            this.getListaGerenteGrid().getStore().load()
                        }
                    }
                }
            },
            {
                el: this.getEl()
            }
        );
    },

    addSelectedGerente: function() {
        if(this.getServico()==undefined){
            console.debug('Botão adicionar gerente de serviço, não há serviço selecionado')
            return '';
        }

        var items = new Array();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Processando...'});
        var store1 = this.getListaGerenteGrid().getStore();
        var selections = this.getGerenteGrid().getSelectionModel().getSelections();

        if(selections.length==0){
            console.debug('Não há gerente selecionado para adicionar ao serviço')
            return '';
        }

        mask.show()

        var rec=store1.getRange()

        for (i=0; i<rec.length; i++){
            items.push(rec[i].get('pk'))
        }

        selections.map(
            function(record) {
                items.push(record.get('pk'))
            }
        );
        this.updateGerentes(items);

    },

    removeSelectedGerente: function() {
        if(this.getServico()==undefined){
            console.debug('Botão excluir gerente de serviço, não há serviço selecionado')
            return '';
        }

        var items = new Array();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Processando...'});
        var store1 = this.getListaGerenteGrid().getStore();
        var selections = this.getListaGerenteGrid().getSelectionModel().getSelections();

        if(selections.length==0){
            console.debug('Não há gerente selecionado para remover do serviço')
            return '';
        }

        mask.show()

        var rec=store1.getRange()

        for (i=0; i<rec.length; i++){
            items.push(rec[i].get('pk'))
        }

        selections.map(
            function(record) {
                items.splice(items.indexOf(record.get('pk')),1)
            }
        );
        this.updateGerentes(items);

    },

    observeServico: function() {
        if(this.ServicoId) {
            this.getTabPanel().enable();

            this.getListaAtendenteGrid().setTitle("Atendentes do serviço "+this.getServicoUnicode())
            this.getListaAtendenteGrid().setFilterProperty('servico', this.getServico());
            this.setStoreAtendenteGrid()

            this.getListaGerenteGrid().setTitle("Gerentes do serviço "+this.getServicoUnicode())
            this.getListaGerenteGrid().setFilterProperty('servicos_vinculados', this.getServico());
            this.setStoreGerenteGrid()
        }
        else {
            this.getTabPanel().disable();
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

            tbar = this._servicoTree.getToolbar()
            // tbar.remove(tbar.getComponent(2)) //Remover

            this._servicoTree.getSelectionModel().on({
                scope: this,
                selectionchange: function(selModel, Node) {
                    if (Node){
                        this.setServico(Node.id, Node.text);
                        this.observeServico();
                    }
                }
            });

            this._servicoTree.getSelectionModel().on({
                scope: this,
                deselect: function() {
                    this.setServico(undefined);
                    this.observeServico();
                }
            });

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
                            title: 'Gerentes',
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
                                this.getGerenteGrid(),
                                this.getControlPanelGerente(),
                                this.getListaGerenteGrid(),
                            ]
                    },
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

        common.siatu.servico.Manager.superclass.constructor.call(this, cfg);
    }
});

