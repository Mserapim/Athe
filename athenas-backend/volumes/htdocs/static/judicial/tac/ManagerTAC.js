/**
 *
 **/
 Ext._define('judicial.tac.ManagerTAC', {
    extend: 'toolkit.widget.TabPanel',

    getGridManagementTac: function() {
        if(!this._GridGestorTac){
            this._GridGestorTac = Ext._create('judicial.tac.ManagementTACGrid', {
                title:'Termo de Ajuste de Conduta',
                region: 'center',
                minHeight: 200,
            });
        }

        var tbar = this._GridGestorTac.getToolbar();
        tbar.insert(4,
            {
                text: 'Assinatura da TAC',
                iconCls: 'icon-diarias icon-ok',
                scope: this,
                handler: this.windowSignature
            }
        );

        this._GridGestorTac.getSelectionModel().on({
            scope: this,
            rowselect: function(sm, index, record) {
                var tacId = record.data.pk;
                this.setManagementTacId(tacId);
            },
            rowdeselect: function(sm) {
                this.setManagementTacId(null);
            }
        });

        this._GridGestorTac.getStore().on({
            scope: this,
            load: function() {
                this.setManagementTacId(null);
            }
        });

        this._GridGestorTac.getStore().on({
            scope: this,
            load: function() {
                var selected = (this._GridGestorTac.getSelectionModel().getSelected());

                if(selected)
                    this.setManagementTacId(selected.get('pk'));
                else
                    this.setManagementTacId(null);
            }
        });

        return this._GridGestorTac;
    },

    windowSignature: function(){
        var selected = this.getGridManagementTac().getSelectionModel().getSelected();
        if (selected)
            Ext._create('judicial.tac.WindowSignature',{
                idTac: selected.get('pk')
            }).show();
        else
            Ext.Msg.show({
                title: 'Notificação',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item.'
            });
    },

    getGridActivity: function() {
        if(!this._gidActivity) {
            this._gidActivity = Ext._create('judicial.tac.ActivityGrid', {
                title: 'Cláusulas a serem cumpridas',
                flex: 1.0,
                border: true,
                columAction: false
            });

        }

        this._gidActivity.getSelectionModel().on({
            scope: this,
            rowselect: function(sm, index, record) {
                this.is_time = record.data.time_type;
                var tacId = record.data.pk;
                this.setActivityId(tacId);
            },
            rowdeselect: function(sm) {
                this.is_time = 0;
                this.setActivityId(null);
            }
        });

        this._gidActivity.getStore().on({
            scope: this,
            load: function() {
                this.is_time = 0;
                this.setActivityId(null);
            }
        });

        this._gidActivity.getStore().on({
            scope: this,
            load: function() {
                var selected = (this._gidActivity.getSelectionModel().getSelected());

                if(selected){
                    this.setActivityId(selected.get('pk'));
                    this.is_time = selected.get('time_type');
                }
                else{
                    this.is_time = 0;
                    this.setActivityId(null);
                }
            }
        });

        return this._gidActivity;
    },

    getGridResponsible: function() {
        if(!this._gridResponsible) {
            this._gridResponsible = Ext._create('judicial.tac.ResponsibleGrid', {
                title: 'Executores da cláusula',
                border: true,
                region: 'south',
                flex:1,
                layout:'fit',
                height:'200',
                minHeight:'200',
                bodyStyle: 'border-right:none',
                split: true,
                hideItemsToolbar: ['add','edit', 'remove', 'download'],
            });
        }

        return this._gridResponsible;
    },

    getParts: function() {
        if(!this._parts) {
            this._parts = Ext._create('rh.person.Grid', {
                title: 'Partes do Procedimento',
                border: true,
                region: 'south',
                flex:1,
                layout:'fit',
                height:'200',
                minHeight:'200',
                bodyStyle: 'border-right:none',
                split: true,
                configOrderToolBar: ['search', '->', 'download'],
            });
        }

        return this._parts;
    },

    setManagementTacId: function(tacId) {
        this.tacId = tacId;
        this._observeTacId();
    },

    setActivityId: function(activityId) {
        this.activityId = activityId;
        this._observeActivityId();
    },

    getActivity: function() {
        return this.activityId;
    },

    _observeTacId: function() {
        if(this.tacId) {
            this.getGridActivity().enable();
            this.getGridActivity().setFilterProperty('tac', this.tacId);
            this.getGridActivity().setParam('tac', this.tacId);

            this.getParts().setFilterProperty('pessoafisica__has_bloke_person__lawsuit__management_tacs', this.tacId, 101);
            this.getParts().setFilterProperty('pessoafisica__has_bloke_government__lawsuit__management_tacs', this.tacId, 101);
            this.getParts().setFilterProperty('pessoajuridica__has_bloke_association__lawsuit__management_tacs', this.tacId, 101);
            this.getParts().setFilterProperty('pessoajuridica__has_bloke_company__lawsuit__management_tacs', this.tacId, 101);
        }
        else {
            this.getGridActivity().getStore().removeAll();
            this.getGridActivity().disable();
            this.getParts().getStore().removeAll();
            this.getParts().disable();
        }
    },

    _observeActivityId: function() {
        if(this.activityId && this.is_time !== 0) {
            this.getGridResponsible().enable();
            this.getParts().enable();
            this.getGridResponsible().setFilterProperty('activity', this.activityId);
            this.getGridResponsible().setParam('activity', this.activityId);
        }
        else {
            this.getGridResponsible().getStore().removeAll();
            this.getGridResponsible().disable();
            this.getParts().disable();
        }
    },

    getControlPanel: function() {
        if(!this._controPanel)
            this._controPanel = Ext._create('Ext.Panel', {
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
                        iconCls: 'icon-siatu icon-siatu-move-left',
                        width: 28,
                        height: 30,
                        style: {
                            padding: '2px 0 0 0'
                        },
                        scope: this,
                        handler: function() {  this.addSelectedResponsible(); }
                    },
                    {
                        xtype: 'panel',
                        height:10,
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
                        handler: function() { this.removeSelectedResponsible(); }
                    },
                    {
                        xtype: 'panel',
                        flex: 1.0
                    }
                ]
            });

        return this._controPanel;
    },

    addSelectedResponsible: function() {
        var items = [];
        var rest = this.getGridResponsible().factoryRestful();
        var activity = this.activityId;
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Processando...'});
        var store1 = this.getGridResponsible().getStore();
        var store2 = this.getParts().getStore();

        // var selections = this.getParts().getSelectionModel().getSelections();
        var selections = this.getParts().getSelectionModel().getSelections();

        if(selections.length === 0){
            console.debug('Não há item selecionado para adicionar');
            return '';
        }

        mask.show();

        selections.map(
            function(record) {
                rest.create(
                    {
                        params: {
                            activity: activity,
                            responsible_person: record.get('pk')
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

    removeSelectedResponsible: function() {
        // if(this.getServico()==undefined){
        //     console.debug('Botão excluir, não há item selecionado')
        //     return '';
        // }
        var rest = this.getGridResponsible().factoryRestful();
        var items = [];
        var selections = this.getGridResponsible().getSelectionModel().getSelections();

        if(selections.length === 0){
            console.debug('Não há atendente selecionado para remover do serviço');
            return '';
        }

        selections.map(
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
                            this.getParts().getStore().reload();
                            this.getGridResponsible().getStore().reload();
                        }
                    }
                }
            },
            {
                el: this.getEl()
            }
        );
    },

    getSeparator: function() {
        if(!this._controlPanelAtendente)
            this._controlPanelAtendente = Ext._create('Ext.Panel', {
                width: 15,
                frame: true,
                layout: 'vbox',
                bodyStyle: {
                    'border-top': 0,
                    'border-bottom': 0
                },
            });

        return this._controlPanelAtendente;
    },

    windowRevision: function() {
        if(this.activityId) {
            Ext._create('judicial.tac.ActivityHistoryRestfulWindow',{
                region:'center',
                scope: this,
                activityId: this.activityId,
                callback: function() {
                    this.getGridActivity().getStore().reload();
                }
            }).show();
        }
        else
            Ext.Msg.show({
                title: 'Notificação',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item.'
            });
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de TACs',
            }
        );

        Ext.apply(
            cfg,
            {
                border: false,
                layout: 'border',
                items: [
                    this.getGridManagementTac(),
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
                            this.getGridActivity(),
                            this.getSeparator(),
                            this.getGridResponsible(),
                            this.getControlPanel(),
                            this.getParts(),
                        ]
                    }
                ]
            }
        );

        this.is_time = 0;

        judicial.tac.ManagerTAC.superclass.constructor.call(this, cfg);
    }
});
