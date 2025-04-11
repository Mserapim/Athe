/**
 *
 **/
Ext._define('common.siatu.chamado.WindowDistribuir', {
    extend: 'core.RestfulWindow',

    rest: 'common.siatu.chamado.Restful',

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: [
                    this.getAtendenteGrid(),
                ]
            });
        return this._formPanel;
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
                height: 300,
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
        this.getAtendenteGrid().reconfigure(store,this.getAtendenteGrid().getColumnModel())
    },

    getButtons: function(cfg) {
        if(!this._buttons) {
            this._buttons = [
                {
                    text: 'Atribuir',
                    scope: this,
                    handler: function() {  this.addSelectedAtendentes() }
                },{
                    text: 'Fechar',
                    scope: this,
                    handler: this.close
                }
            ];
        }
        return this._buttons;
    },

    addSelectedAtendentes: function() {
        var items = new Array();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Processando...'});
        var selections = this.getAtendenteGrid().getSelectionModel().getSelections();

        if(selections.length==0){
            console.debug('Não há atendente selecionado para adicionar ao chamado')
            return '';
        }

        mask.show()

        selections.map(
            function(record) {
                items.push(record.get('pk'))
            }
        );
        this.update(items);
    },

    update: function(items){
        var rest = this.factoryRestfulChamado();
        for (var i=0; i<this.chamados.length; i++) {
            rest.update(
                this.chamados[i],{
                    params: {
                        atendentes: items,
                    },
                    externalCallback: {
                        scope: this,
                        success: {
                            scope: this,
                            fn: function() {
                                this.close();
                            }
                        }
                    }
                },{
                    el: this.getEl()
                }
            );
        }
    },

    factoryRestfulChamado: function() {
        if(!this._restful)
            this._restful = Ext._create('common.siatu.chamado.Restful', {});
        return this._restful;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        this.setStoreAtendenteGrid(cfg.params.chamados[0].data.pk);

        var chamados_id = new Array();
        for (var i=0; i<cfg.params.chamados.length; i++) {
            chamados_id.push(cfg.params.chamados[i].data.pk);
        }
        this.chamados = chamados_id;

        common.siatu.chamado.WindowDistribuir.superclass.constructor.call(this, cfg);
    }
});
