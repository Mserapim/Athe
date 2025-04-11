
Ext._define('judicial.parts.ConfidentialAccessWindow', {
    extend: 'judicial.PartLawsuitActionWindow',

    rest: undefined,

    autoCreate: true,

    getControlPanel: function(cfg) {
        if(!this._controlPanel)
            this._controlPanel = Ext._create('Ext.Panel', {
                width: 40,
                height: 600,
                boder: false,
                frame: true,
                layout: 'vbox',
                bodyStyle: {
                    'border-top': 0,
                    'border-bottom': 0,
                },
                items: [
                    {
                        xtype: 'panel',
                        flex: 1.0
                    },

                    {
                        xtype: 'button',
                        iconCls: 'icon-core icon-core-add-selected',
                        width: 28,
                        height: 30,
                        style: {
                            padding: '2px 0 0 0',
                        },
                        scope: this,
                        handler: function() { this.markerPartLawsuit(); }
                    },

                    {
                        xtype: 'button',
                        iconCls: 'icon-core icon-core-remove-selected',
                        width: 28,
                        height: 30,
                        style: {
                            padding: '2px 0 0 0',
                        },
                        scope: this,
                        handler: function() { this.unmarkerPartLawsuit(); }
                    },
                    {
                        xtype: 'panel',
                        flex: 1.0
                    }
                ]
            });

        return this._controlPanel;
    },

    _markerPartLawsuit: function(pkset) {
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Marcando o documento...'});

        mask.show();
        rest.markerPartLawsuit(
            this.oId,
            pkset,
            {
                scope: this,
                fn: function() {
                    this.getPartLawsuitGrid().getStore().reload();
                    this.getPartLawsuitSelectedGrid().getStore().reload();
                }
            },
            {
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Marcando o documento...',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    markerPartLawsuit: function() {
        selected = this.getPartLawsuitGrid().getSelectionModel().getSelections();
        if(selected.length > 0)
            this._markerPartLawsuit(selected.map(function(data) { return data.get('pk'); }));
        else
            Ext.Msg.show({
                title: 'Selecionando documento',
                msg: 'Primeiro selecione o documento que deseja marcar.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    _unmarkerPartLawsuit: function(pkset) {
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Desmarcando o documento..'});

        mask.show();
        rest.unmarkerPartLawsuit(
            this.oId,
            pkset,
            {
                scope: this,
                fn: function() {
                    this.getPartLawsuitGrid().getStore().reload();
                    this.getPartLawsuitSelectedGrid().getStore().reload();
                }
            },
            {
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Desmarcando o documento...',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    unmarkerPartLawsuit: function(selected) {
        selected = this.getPartLawsuitSelectedGrid().getSelectionModel().getSelections();

        if(selected.length > 0)
            this._unmarkerPartLawsuit(selected.map(function(data) { return data.get('pk'); }));
        else
            Ext.Msg.show({
                title: 'Selecionando documento',
                msg: 'Primeiro selecione o documento que deseja desmarcar.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    getPartLawsuitSelectedGrid: function(cfg) {
        if(!this._lawsuitMarkerGrid) {
            var me = this;
            this._lawsuitMarkerGrid = Ext._create('judicial.PartLawsuitGrid', {
                title: 'Documentos marcados',
                toolbarHideLabel: true,
                flex: 1.0,
                minWidth: 345,
                doubleClickHandler: function() {
                    me.unmarkerPartLawsuit();
                },
                border: false,
                frame: false,
                gridAutoLoad: false,
                configOrderToolBar: ['search'],
                columnAction: false,
            });

            this._lawsuitMarkerGrid.setFilterProperty('lawsuit', (cfg.params || this.params).lawsuit || 0, 1, false);
        }

        return this._lawsuitMarkerGrid;
    },

    getPartLawsuitGrid: function(cfg) {
        if(!this._partlawsuitGrid) {
            var me = this;
            this._partlawsuitGrid = Ext._create('judicial.PartLawsuitGrid', {
                title: 'Documentos',
                toolbarHideLabel: true,
                flex: 1.0,
                minWidth: 345,
                doubleClickHandler: function() {
                    me.markerPartLawsuit();
                },
                border: false,
                frame: false,
                gridAutoLoad: false,
                configOrderToolBar: ['search',],
                columnAction: false,
            });

            this._partlawsuitGrid.setFilterProperty('signed_at__isnull', false, 1, false);
            this._partlawsuitGrid.setFilterProperty('lawsuit', (cfg.params || this.params).lawsuit || 0, 2, false);
        }

        return this._partlawsuitGrid;
    },
    
    confidential: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);
    
        if(value !== undefined) {
            this._confidential = value;
    
            if(dispatch) this.observer();
        }
    
        return this._confidential;
    },

    observer: function() {
        console.log('Abstract');
    },

    getApplyInField: function(cfg) {
        if(!this._applyInField) {
            this._applyInField = Ext._create('Ext.form.RadioGroup', {
                xtype: 'radiogroup',
                fieldLabel: 'Decretar sigilo',
                columns: 2,
                vertical: true,
                items: [
                    {boxLabel: 'No Procedimento', name: 'apply_in', inputValue: 1},
                    {boxLabel: 'Em documento', name: 'apply_in', inputValue: 2},
                ]
            });

           this._applyInField.on({
                scope: this,
                change: function(me, checked) {
                    this.selection(checked.inputValue);
                }
            });
        }
        return this._applyInField;
    },
    
    selection: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);
        if(!this._selection)
            this._selection = this.getApplyInField().getValue();
    
        if(value !== undefined) {
            this._selection = value;
    
            if(dispatch) this.observer();
        }
    
        return this._selection;
    },

    getMainPanel: function(cfg){
        if(!this._mainTab)
            this._mainTab = Ext._create('Ext.Panel',{
                layout: 'form',
                title: cfg.title,
                border: false,
                frame: false,
                scope: this,
                height: 520,
                items: [
                    {
                        xtype: 'panel',
                        layout: 'form',
                        border: false,
                        frame: true,
                        height: 40,
                        layout: {
                            type:'hbox',
                            align: 'stretch'
                        },
                        items: [
                            this.getApplyInField(cfg)
                        ]
                    }, 
                    {
                        xtype: 'panel',
                        layout: 'form',
                        border: false,
                        frame: true,
                        height: 480,
                        layout: {
                            type:'hbox',
                            align: 'stretch'
                        },
                        items: [
                            this.getPartLawsuitGrid(cfg),
                            this.getControlPanel(),
                            this.getPartLawsuitSelectedGrid(cfg)
                        ]
                    }
                ]
            });
        return this._mainTab;
    },

    getTabPanelItems: function(cfg){
        return [
            this.getMainPanel(cfg)
        ];
    },

    getTabPanel: function(cfg) {
        if(!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                xtype: 'tabpanel',
                activeTab: 0,
                frame: false,
                border: false,
                items: this.getTabPanelItems(cfg)
            });

        return this._tabPanel;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: false,
                items: this.getTabPanel(cfg)
            });

        return this._formPanel;
    },

    readInstance: function(instance) {
        this.getFormPanel().getForm().setValues(instance);
        this.confidential((this.oId || 0), true);
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        
        Ext.applyIf(cfg, {
            title: 'undefined'
        });

        Ext.apply(cfg, {
            border: false,
            buttonAlign: 'left',
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.oId = instance.pk;
                    this.action = 'update';
                    this.readInstance(instance);
                }
            }
        });

        judicial.parts.ConfidentialAccessWindow.superclass.constructor.call(this, cfg);

        this.on({
            afterrender: function(me) {
                this.confidential((this.oId || 0), true);
            }
        });
        
    }

});

