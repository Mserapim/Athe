/**
 *
 **/
Ext._define('common.siatu.chamado.TabDistribuicaoManual', {
    extend: 'Ext.Panel',

    setChamado: function(pk) {
        this.ChamadoId = pk;
    },

    getChamado: function() {
        return this.ChamadoId;
    },

    getListaAtendenteGrid: function() {
        if(!this._listaAtendenteGrid){
            this._listaAtendenteGrid = Ext._create('common.siatu.atendente.Grid', {
                flex: 1.0,
                border: false,
                gridAutoLoad: false,
                title:'Atendentes do chamado',
                columnAction: false,
                allowCreate: false,
                allowRemove: false,
                hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'notificacao']
            });

        }

         return this._listaAtendenteGrid;
    },

    getAtendenteGrid: function() {
        if(!this._atendenteGrid) {
            this._atendenteGrid = Ext._create('common.siatu.atendente.Grid', {
                title: 'Atendentes',
                flex: 1.0,
                border: true,
                columnAction:false,
                gridAutoLoad:false,
                allowCreate: false,
                allowRemove: false,
                hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'notificacao']
            });
        }

        return this._atendenteGrid;
    },

    setStoreAtendenteGrid: function(chamado) {
        rest = Ext._create('common.siatu.atendente.Restful',{});
        store = Ext._create('Ext.data.Store', {
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        api: {
                            read: core.callAction("SiatuAtendente", "action_atendentes_not_in_chamado", chamado)
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

        this.getAtendenteGrid().setStore(store)
        this.getAtendenteGrid().reconfigure(
            store,
            this.getAtendenteGrid().getColumnModel()
        )
    },

    factoryRestfulChamado: function() {
        if(!this._restful)
            this._restful = Ext._create('common.siatu.chamado.Restful', {});

        return this._restful;
    },

    update: function(items){
        var chamado = this.getChamado();
        var rest = this.factoryRestfulChamado();
        rest.update(
            chamado,{
                params: {
                    atendentes: items,
                },
                externalCallback: this.callback
            },
            {
                el: this.getEl()
            }
        );
    },

    addSelectedAtendente: function() {
        var items = new Array();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Processando...'});
        var store1 = this.getListaAtendenteGrid().getStore();
        var selections = this.getAtendenteGrid().getSelectionModel().getSelections();

        if(selections.length==0){
            console.debug('Não há atendente selecionado para adicionar ao chamado')
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
        this.update(items);
    },

    removeSelectedAtendente: function() {
        var items = new Array();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Processando...'});
        var store1 = this.getListaAtendenteGrid().getStore();
        var selections = this.getListaAtendenteGrid().getSelectionModel().getSelections();

        if(selections.length==0){
            console.debug('Não há atendente selecionado para remover do chamado')
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
        this.update(items);
    },

    getControlPanel: function() {
        if(!this._controlPanelAtendente)
            this._controlPanelAtendente = Ext._create('Ext.Panel', {
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
                        text: '',
                        iconCls: 'icon-siatu icon-siatu-move-right',
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
                        height:10,
                    },
                    {
                        xtype: 'button',
                        text: '',
                        iconCls: 'icon-siatu icon-siatu-move-left',
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

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getListaAtendenteGrid().getStore().reload();
                            this.setStoreAtendenteGrid(this.getChamado())
                        }
                    }
                }
            }
        );

        Ext.apply(
            cfg,
            {
                title: 'Distribuição Manual',
                layout: 'hbox',
                split:true,
                bodyStyle: {
                    'border-left': 0,
                    'border-right': 0
                },
                layoutConfig: {
                    align: 'stretch',
                },
                items:[
                    this.getAtendenteGrid(),
                    this.getControlPanel(),
                    this.getListaAtendenteGrid(),
                ]
            }
        );

        common.siatu.chamado.TabDistribuicaoManual.superclass.constructor.call(this, cfg);
    }

});
