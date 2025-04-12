/**
 *
 **/
Ext._define('common.siatu.chamado.transferencia.PanelGerentes', {
    extend: 'Ext.Panel',

    setParam: function(key, value) {
        this.params = core.nullValue(this.params, {});
        this.params[key] = value;
    },

    getParams: function() {
        return core.nullValue(this.params, {});
    },

    setChamado: function(pk) {
        this.ChamadoId = pk;
    },

    getChamado: function() {
        return this.ChamadoId;
    },

    getListaAtendenteGrid: function() {
        if(!this._listaAtendenteServGrid){
             this._listaAtendenteServGrid = Ext._create('common.siatu.atendente.Grid', {
                flex: 1.0,
                border: true,
                gridAutoLoad: false,
                title:'Lista de atendentes do chamado',
                columnAction: false,
                allowCreate: false,
                allowRemove: false,
                hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'notificacao']
            });

            this._listaAtendenteServGrid.getStore().setDefaultSort('username','ASC');

            this._listaAtendenteServGrid.getKeywordField().setWidth(210);

            var fbar = this._listaAtendenteServGrid.getFooterbar();
            fbar.remove(fbar.getComponent(10)); //Atualizar Store

         }

         return this._listaAtendenteServGrid;
    },

    getAtendenteGrid: function() {
        if(!this._atendenteGrid) {
            this._atendenteGrid = Ext._create('common.siatu.atendente.Grid', {
                title: 'Atendentes',
                flex: 1.0,
                border: true,
                columnAction:false,
                layout: 'fit',
                gridAutoLoad: false,
                allowCreate: false,
                allowRemove: false,
                hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'notificacao']
            });

            this._atendenteGrid.getKeywordField().setWidth(210);

            var fbar = this._atendenteGrid.getFooterbar();
            fbar.remove(fbar.getComponent(10)); //Atualizar Store
        }

        return this._atendenteGrid;
    },

    setStoreAtendenteGrid: function(chamado) {
        rest = Ext._create('common.siatu.atendente.Restful',{});
        this.getAtendenteGrid().setStore(
            Ext._create('Ext.data.Store', {
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        api: {
                            read: core.callAction("SiatuAtendente", "action_atendentes_not_in_chamado", chamado)
                        },
                        disableCaching: false,
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
        );
        var store = this.getAtendenteGrid().getStore()
        store.setDefaultSort('username','ASC')
        this.getAtendenteGrid().reconfigure(store,this.getAtendenteGrid().getColumnModel())
    },

    addSelectedAtendente: function() {
        var items = new Array();
        var store1 = this.getListaAtendenteGrid().getStore();
        var store2 = this.getAtendenteGrid().getStore();
        var selections = this.getAtendenteGrid().getSelectionModel().getSelections();

        if(selections.length==0){
            console.debug('Não há atendente selecionado para adicionar ao chamado')
            return '';
        }

        selections.map(
            function(record) {
                store1.addSorted(record)
                store2.remove(record)
            }
        );

        this.getAtendenteGrid().getView().refresh()
        this.getListaAtendenteGrid().getView().refresh()

        var rec=store1.getRange()

        for (i=0; i<rec.length; i++){
            items.push(rec[i].get('pk'))
        }

        this.setParam('atendente_posterior',items)
    },

    removeSelectedAtendente: function() {
        var items = new Array();
        var store1 = this.getListaAtendenteGrid().getStore();
        var store2 = this.getAtendenteGrid().getStore();
        var selections = this.getListaAtendenteGrid().getSelectionModel().getSelections();

        if(selections.length==0){
            console.debug('Não há atendente selecionado para remover do chamado')
            return '';
        }

        selections.map(
            function(record) {
                store1.remove(record)
                store2.addSorted(record)
            }
        );

        this.getAtendenteGrid().getView().refresh()
        this.getListaAtendenteGrid().getView().refresh()

        var rec=store1.getRange()

        for (i=0; i<rec.length; i++){
            items.push(rec[i].get('pk'))
        }


        this.setParam('atendente_posterior',items)
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

        Ext.apply(
            cfg,
            {
                layout:'form',
                labelWidth:50,
                items:[{
                    region: 'center',
                    layout: 'hbox',
                    split:true,
                    height:310,
                    bodyStyle: {
                        'border-left': 0,
                        'border-right': 0,
                    },
                    // layoutConfig: {
                    // align: 'stretch',
                    // },
                    defaults:{
                        height:300,
                    },
                    items:[
                        this.getAtendenteGrid(),
                        this.getControlPanel(),
                        this.getListaAtendenteGrid(),
                    ]
                    },
                    {
                        region: 'south',
                        xtype: 'textfield',
                        name: 'motivo',
                        fieldLabel: 'Motivo',
                        width: 700,
                        allowBlank: false,
                    }
                ]
            }
        );

        common.siatu.chamado.transferencia.PanelGerentes.superclass.constructor.call(this, cfg);
        this.setParam('atendente_posterior','old')
    }

});