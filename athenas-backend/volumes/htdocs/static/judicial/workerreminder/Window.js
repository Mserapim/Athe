Ext._define('judicial.workerreminder.Window', {
    extend: 'Ext.Window',

    width: 800,

    _addReceiver: function(pkset) {
        this.receiverSelected(pkset);
    },

    addReceiver: function(selected) {
        selected = (selected || this.getReceiverGrid().getSelectionModel().getSelections());
        if(selected.length > 0)
            this._addReceiver(selected.map(function(data) { return data.get('pk'); }));
        else
            Ext.Msg.show({
                title: 'Adicionando itens',
                msg: 'Primeiro selecione os itens que deseja adicionar.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    _removeReceiver: function(pkset) {
        this.receiverSelected(pkset, true)
    },

    removeReceiver: function(selected) {
        selected = (selected || this.getReceiverSelectedGrid().getSelectionModel().getSelections());

        if(selected.length > 0)
            this._removeReceiver(selected.map(function(data) { return data.get('pk'); }));
        else
            Ext.Msg.show({
                title: 'Adicionando itens',
                msg: 'Primeiro selecione os itens que deseja remover.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    getControlPanel: function() {
        if(!this._controlPanel)
            this._controlPanel = Ext._create('Ext.Panel', {
                width: 40,
                height: 200,
                frame: false,
                layout: 'vbox',
                bodyStyle: {
                    'border-top': 0,
                    'border-bottom': 0,
                    'margin': '5px'
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
                        handler: function() { this.addReceiver(); }
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
                        handler: function() { this.removeReceiver(); }
                    },
                    {
                        xtype: 'panel',
                        flex: 1.0
                    }
                ]
            });

        return this._controlPanel;
    },

    getReceiverSelectedGrid: function() {
        if(!this._receiverSelectedGrid) {
            var me = this;
            this._receiverSelectedGrid = Ext._create('rh.employee.Grid', {
                title: 'Destinatários Selecionados',
                flex: 1.0,
                height: 240,
                doubleClickHandler: function() {
                    me.removeReceiver();
                },
                border: false,
                frame: false,
                gridAutoLoad: false,
                configOrderToolBar: ['-', '->', '-'],
                columnAction: false,
                hiddenFilter: true,
                hideColumns: ['pk', 'ativo', 'matricula', 'afastamento', 'cargo', 'matricula', 'departure_unicode', 'effective_unicode', 'commission_unicode', 'elective_unicode']
            });

            this._receiverSelectedGrid.setFilterProperty('pk__in', [], 100, true);

        }

        return this._receiverSelectedGrid;
    },

    getReceiverGrid: function() {
        if(!this._receiverGrid) {
            var me = this;
            this._receiverGrid = Ext._create('rh.employee.Grid', {
                title: 'Destinatários Disponíveis',
                flex: 1.0,
                height: 240,
                doubleClickHandler: function() {
                    me.addReceiver();
                },
                border: false,
                frame: false,
                gridAutoLoad: true,
                configOrderToolBar: ['search',],
                columnAction: false,
                hiddenFilter: true,
                hideColumns: ['pk', 'ativo', 'matricula', 'afastamento', 'cargo', 'matricula', 'departure_unicode', 'effective_unicode', 'commission_unicode', 'elective_unicode']
            });

            this._receiverGrid.setFilter([{property: 'ativo', value: true, stage: 100}]);
        }

        return this._receiverGrid;
    },

    getPartsGrid: function(cfg) {
        if(!this._partsGrid) {
            this._partsGrid = Ext._create('judicial.PartLawsuitGrid', {
                height: 150,
                border: true,
                frame: true,
                gridAutoLoad: true,
                configOrderToolBar: [],
                columnAction: false,
                doubleClickHandler: function() {},
            });

            this._partsGrid.setFilterProperty('pk__in', cfg.params.parts, 100);
        }

        return this._partsGrid;
    },

    receiverSelected: function(value, remove) {
        remove = core.nullValue(remove, false);

        if(value !== undefined) {
            if(remove) {
                this._receiverSelected = (this._receiverSelected || []).filter(function(n) {
                    return value.indexOf(n) === -1;
                });
            } else
                this._receiverSelected = (this._receiverSelected || []).concat(value);

            this.observerReceiver();
        }

        return this._receiverSelected;
    },

    observerReceiver: function() {
        var value = this.receiverSelected();

        if(value) {
            this.getReceiverSelectedGrid().setFilterProperty('pk__in', value, 100);
            this.getReceiverGrid().setFilterProperty('pk__in', value, -100);
        } else {
            this.getReceiverSelectedGrid().setFilterProperty('pk__in', [], 100, false);
            this.getReceiverSelectedGrid().getStore().removeAll();
        }
    },

    newObject: function() {
        var rest = Ext._create('judicial.workerreminder.Restful');
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Criando comunicação...'});
        var values = this.getFormPanel().getForm().getValues();

        values.parts = this.params.parts;
        values.receiver = this.receiverSelected();

        mask.show();
        rest.newObject(
            values,
            {
                scope: this,
                fn: function(rst) {
                    if(rst.success) {
                        core.invokeCallback((this.callback || {}).success);
                        this.close();

                        Ext.Msg.show({
                            title: 'Criando comunicação',
                            msg: rst.message,
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK
                        });
                    }
                    else
                        Ext.Msg.show({
                            title: 'Criando comunicação',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Criando comunicação',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    getMainPanel: function(cfg) {
        if(!this._mainPanel)
            this._mainPanel = Ext._create('Ext.Panel', {
                layout: {
                    type: 'vbox',
                    align: 'stretch'
                },
                border: false,
                frame: false,
                height: 400,
                items: [
                    this.getPartsGrid(cfg),
                    {
                        xtype: 'panel',
                        region: 'center',
                        layout: 'hbox',
                        bodyStyle: {
                            'border-left': 0,
                            'border-right': 0
                        },
                        frame: true,
                        items: [
                            this.getReceiverGrid(),
                            this.getControlPanel(),
                            this.getReceiverSelectedGrid()
                        ]
                    },
                ]
            });

        return this._mainPanel;
    },

    getFieldsPanel: function(cfg) {
        if(!this._fieldsPanel)
            this._fieldsPanel = Ext._create('Ext.Panel', {
                frame: true,
                border: false,
                layout: 'form',
                items: [
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Observação'
                    },
                    {
                        xtype: "ckeditor",
                        allowBlank: true,
                        fieldLabel: "Observação",
                        name: "observation",
                        hideLabel: true,
                        height: 150,
                        submit: true,
                    },
                    {
                        xtype: 'container',
                        width: 600,
                        layout: {
                            type: 'hbox',
                            align: 'stretchmax'
                        },
                        items: [
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 2.75,
                                items: [
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: 'Prioridade',
                                        width: 150,
                                        hiddenName: 'priority',
                                        choiceId: 'judicial.WORKER_REMINDER_PRIORITY',
                                        value: 1
                                    },
                                ]
                            },
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 1.25,
                                labelWidth: 50,
                                items: [
                                    {
                                        xtype: "datefield",
                                        allowBlank: true,
                                        fieldLabel: "Prazo",
                                        name: "deadline",
                                        width: 100,
                                    },
                                ]
                            }
                        ]
                    },
                ]
            });

        return this._fieldsPanel;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: false,
                items: [
                    this.getMainPanel(cfg),
                    this.getFieldsPanel(cfg)
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Comunicar',
            border: false
        });

        Ext.apply(cfg, {
            width: 900,
            items: [
                this.getFormPanel(cfg)
            ],
            buttons: [
                {
                    text: 'Comunicar',
                    scope: this,
                    handler: function() { this.newObject(); }

                },
                {
                    text: 'Cancelar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ]
        });

        judicial.workerreminder.Window.superclass.constructor.call(this, cfg);
        this.observerReceiver();
    }
});
