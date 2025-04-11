/**
 *
 **/
Ext._define('common.siatu.chamado.TabTerceiroInterno', {
    extend: 'Ext.Panel',

    setChamado: function(pk) {
        this.ChamadoId = pk;
    },

    getChamado: function() {
        return this.ChamadoId;
    },

    getListaTerceiroGrid: function() {
        if(!this._listaTerceiroGrid){
            this._listaTerceiroGrid = Ext._create('common.siatu.terceiro.Grid', {
                flex: 1.0,
                border: false,
                gridAutoLoad: false,
                title:'Lista de terceiros do chamado',
                columnAction: false,
            });

            var tbar = this._listaTerceiroGrid.getToolbar()
            tbar.remove(tbar.getComponent(0)); // Adicionar
            tbar.remove(tbar.getComponent(0)); // Editar
            tbar.remove(tbar.getComponent(0)); // Remover
            tbar.remove(tbar.getComponent(0)); //Separador

        }

         return this._listaTerceiroGrid;
    },

    getTerceiroGrid: function() {
        if(!this._terceiroGrid) {
            this._terceiroGrid = Ext._create('common.siatu.terceiro.Grid', {
                title: 'Terceiros',
                flex: 1.0,
                border: true,
                columnAction:false,
                gridAutoLoad:false,
                storeDisableCaching: false
            });

            var tbar = this._terceiroGrid.getToolbar()
            tbar.remove(tbar.getComponent(0)); // Adicionar
            tbar.remove(tbar.getComponent(0)); // Editar
            tbar.remove(tbar.getComponent(0)); // Remover
            tbar.remove(tbar.getComponent(0)); // Separador
        }

        return this._terceiroGrid;
    },

    setStoreTerceiroGrid: function(chamado) {
        rest = Ext._create('common.siatu.terceiro.Restful',{});
        store = Ext._create('Ext.data.Store', {
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        api: {
                            read: core.callAction("SiatuTerceiroInterno", "action_terceiros_not_in_chamado", chamado)
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

        this.getTerceiroGrid().setStore(store)
        this.getTerceiroGrid().reconfigure(
            store,
            this.getTerceiroGrid().getColumnModel()
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
                    terceiro_interno: items,
                },
                externalCallback: this.callback
            },
            {
                el: this.getEl()
            }
        );
    },

    addSelected: function() {
        var items = new Array();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Processando...'});
        var store1 = this.getListaTerceiroGrid().getStore();
        var selections = this.getTerceiroGrid().getSelectionModel().getSelections();

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

    removeSelected: function() {
        var items = new Array();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Processando...'});
        var store1 = this.getListaTerceiroGrid().getStore();
        var selections = this.getListaTerceiroGrid().getSelectionModel().getSelections();

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
                        text: '',
                        iconCls: 'icon-siatu icon-siatu-move-right',
                        width: 28,
                        height: 30,
                        style: {
                            padding: '2px 0 0 0'
                        },
                        scope: this,
                        handler: function() {  this.addSelected() }
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
                        handler: function() { this.removeSelected()}
                    },
                    {
                        xtype: 'panel',
                        flex: 1.0
                    }
                ]
            });

        return this._controlPanel;
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
                            this.getListaTerceiroGrid().getStore().reload();
                            this.setStoreTerceiroGrid(this.getChamado())
                        }
                    }
                }
            }
        );

        Ext.apply(
            cfg,
            {
                title: 'Terceiro Interno',
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
                    this.getTerceiroGrid(),
                    this.getControlPanel(),
                    this.getListaTerceiroGrid(),
                ]
            }
        );

        common.siatu.chamado.TabTerceiroInterno.superclass.constructor.call(this, cfg);
    }

});
