Ext._define('planning.hiring.minutesolicitation.MinuteSolicitationItemWindow', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.minutesolicitation.MinuteSolicitationItemRestful',

    relatedName: undefined,
    width: 1000,

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                autoHeigth: true,
                labelAlign: 'top',
                items: [
                    {
                        layout: 'column',
                        items: [
                            {
                                columnWidth: '0.2',
                                layout: 'form',
                                items: [
                                    this.getSolicitationItem(cfg),
                                ],
                            },
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items: [
                                    this.displayDescriptionItem(),
                                ]
                            },
                            {
                                columnWidth: '0.2',
                                layout: 'form',
                                items: [
                                    this.showItemBalance(),
                                ],
                                anchor: '90%'
                            },
                            {
                                columnWidth: '0.1',
                                layout: 'form',
                                items: [
                                    {
                                        allowBlank: false,
                                        fieldLabel: "Qtde Solicitada",
                                        name: "quantity",
                                        xtype: "numberfield",
                                        anchor: '90%',
                                        tabIndex: 2
                                    },
                                ]
                            },


                        ]

                    },
                    this.getMainComplementaryDescriptionPanel(cfg),
                    this.displayMinuteSolicitationItemGrid(cfg)
                ]
            });

        return this._formPanel;
    },

    getSolicitationItem: function (cfg) {
        if (!this._fieldSolicitationItem) {
            this._fieldSolicitationItem = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Item',
                rest: "planning.hiring.minuteitem.MinuteItemRestful",
                name: 'item',
                anchor: '90%',
                tabIndex: 1,
                minChars: 1,
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar: ['add', 'edit', 'remove', 'disable', '-', 'import', 'download'],
                    listeners: {
                        scope: this,
                        render: function (grid) {
                            tbar = grid.getToolbar();
                            tbar.remove(tbar.getComponent(1));//Item/Linha
                            tbar.remove(tbar.getComponent(0));//Novo
                        },
                    }
                },
                preFilter: [
                    { property: 'minute', value: cfg.params.minute, stage: 100 },
                    { property: 'quantity__isnull', value: false, stage: 101 },
                    { property: 'status__in', value: [1, 4], stage: 102 },
                ],
                comboListeners: {
                    scope: this,
                    select: {
                        buffer: 1,
                        fn: function (combo) {
                            Ext.Ajax.request({
                                scope: this,
                                url: toolkit.util.Normalize.controller_action(
                                    'PHMMinuteItem',
                                    'get_item_values'
                                ),
                                params: {
                                    pk: combo.getValue()
                                },
                                success: function (response) {
                                    var rst = Ext.decode(response.responseText);
                                    if (rst.success) {
                                        this.showItemBalance().setValue(rst.item_balance);
                                        this.displayDescriptionItem().setValue(rst.item_description);
                                    }
                                    else
                                        Ext.Msg.show({
                                            title: 'Buscando saldo disponível',
                                            icon: Ext.Msg.INFO,
                                            buttons: Ext.Msg.OK,
                                            msg: rst.message
                                        });
                                },
                                failure: function (response) {
                                    Ext.Msg.show({
                                        title: 'Buscando saldo disponível',
                                        icon: Ext.Msg.INFO,
                                        buttons: Ext.Msg.OK,
                                        msg: rst.message
                                    });
                                }

                            });

                            this.getComplementaryDescriptionGrid().setFilterProperty('minuteitem', combo.getValue(), 0);

                        },
                    },
                    render: function (field) {
                        field.focus(false, 500);
                    }
                }
            });
        }

        return this._fieldSolicitationItem;
    },

    showItemBalance: function () {
        if (!this._itemBalance)
            this._itemBalance = Ext._create('Ext.form.DisplayField', {
                fieldLabel: 'Saldo Disponível',
                name: 'item_balance'
            });
        return this._itemBalance;
    },

    displayDescriptionItem: function () {
        if (!this._descriptionItem)
            this._descriptionItem = Ext._create('Ext.form.DisplayField', {
                fieldLabel: 'Descrição do Item',
                name: 'item_unicode',
                anchor: '90%'
            });

        return this._descriptionItem;
    },

    createComplementaryDescription: function (selected) {

        var rest = this.getComplementaryDescriptionAddedGrid().factoryRestful();
        var solicitation_item_value = this.getComplementaryDescriptionAddedGrid().getParams().solicitation_item;
        var me = this;

        selected = (selected || this.getComplementaryDescriptionGrid().getSelectionModel().getSelections());

        if (selected.length > 0) {
            selected.map(
                function (data) {
                    rest.create(
                        {
                            params: {
                                solicitation_item: solicitation_item_value,
                                item_description: data.get('pk')
                            },
                            externalCallback: {
                                success: {
                                    fn: function (request) {
                                        me.getComplementaryDescriptionAddedGrid().getStore().reload();
                                        me.getComplementaryDescriptionGrid().getStore().reload();
                                    }
                                }

                            }
                        }

                    );
                }
            );

        } else
            Ext.Msg.show({
                title: 'Selecionar Descrição Complementar',
                msg: 'Primeiro selecione a descrição que deseja marcar.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    deleteComplementaryDescription: function (selected) {
        var rest = this.getComplementaryDescriptionAddedGrid().factoryRestful();
        var me = this;
        selected = (selected || this.getComplementaryDescriptionAddedGrid().getSelectionModel().getSelections());

        if (selected.length > 0) {
            pk = selected.map(function (selected) { return selected.get('pk'); });

            rest.remove(
                false,
                {
                    params: {
                        filter: Ext.encode([
                            { 'property': 'pk__in', 'value': pk }
                        ])
                    },
                    externalCallback: {
                        success: {
                            fn: function () { me.getComplementaryDescriptionAddedGrid().getStore().reload(); },
                        }
                    }
                },
                {
                    el: this.getEl(),
                    msg: 'Removendo item.'
                }
            );
        }
        else
            Ext.Msg.show({
                title: 'Selecionar Descrição Complementar',
                msg: 'Primeiro selecione a descrição que deseja desmarcar.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    getComplementaryDescriptionGrid: function (cfg) {
        if (!this._complementaryDescriptionGrid) {
            var me = this;
            this._complementaryDescriptionGrid = Ext._create('planning.hiring.minuteitem.MinuteItemComplementaryDescriptionGrid', {
                title: 'Descrição Complementar',
                border: false,
                columnAction: false,
                flex: 1.0,
                minWidth: 200,
                height: 200,
                hideItemsToolbar: ['add', 'edit', 'remove', '-', 'filter', 'search', 'download'],
                doubleClickHandler: function () {
                    me.createComplementaryDescription();
                }
            });

            this._complementaryDescriptionGrid.setFilterProperty('minuteitem', cfg.values.item, 0);

        }

        return this._complementaryDescriptionGrid;
    },

    getComplementaryDescriptionAddedGrid: function (cfg) {
        if (!this._complementaryDescriptionMarkedGrid) {
            var me = this;
            this._complementaryDescriptionMarkedGrid = Ext._create('planning.hiring.minutesolicitation.MinuteSolicitationItemDescriptionGrid', {
                title: 'Descrição Complementar Selecionada',
                border: false,
                flex: 1.0,
                minWidth: 300,
                height: 200,
                hideItemsToolbar: ['add', 'edit', 'remove', '-', 'filter', 'search', 'download'],
                doubleClickHandler: function () {
                    me.deleteComplementaryDescription();
                },
            });
        }

        return this._complementaryDescriptionMarkedGrid;
    },

    getControlPanel: function () {
        if (!this._controlPanel)
            this._controlPanel = Ext._create('Ext.Panel', {
                width: 40,
                height: 200,
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
                        handler: function () { this.createComplementaryDescription(); }
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
                        handler: function () { this.deleteComplementaryDescription(); }
                    },
                    {
                        xtype: 'panel',
                        flex: 1.0
                    }
                ]
            });

        return this._controlPanel;
    },

    getMainComplementaryDescriptionPanel: function (cfg) {
        if (!this._mainComplementaryDescriptionPanel)
            this._mainComplementaryDescriptionPanel = Ext._create('Ext.Panel', {
                layout: 'hbox',
                align: 'stretch',
                height: 210,
                border: false,
                items: [
                    this.getComplementaryDescriptionGrid(cfg),
                    this.getControlPanel(),
                    this.getComplementaryDescriptionAddedGrid(cfg),
                ]
            });

        return this._mainComplementaryDescriptionPanel;
    },

    displayMinuteSolicitationItemGrid: function (cfg) {
        if (!this._displayMinuteSolicitationItemGrid) {
            this._displayMinuteSolicitationItemGrid = Ext._create('planning.hiring.minutesolicitation.MinuteSolicitationItemGrid', {
                title: 'Itens Adicionados',
                region: 'center',
                frame: true,
                height: 300,
                hideItemsToolbar: ['add', 'edit', 'remove', '-', 'filter', 'search', 'download'],
            });
            this._displayMinuteSolicitationItemGrid.setFilterProperty('solicitation', cfg.values.solicitation, 0);
        }

        return this._displayMinuteSolicitationItemGrid;
    },

    solicitationitem: function (value, observe) {
        observe = (observe === undefined ? true : observe);


        if (value !== undefined) {

            this._solicitationItem = value;

            if (observe)
                this.observer();
        }
        return this._solicitationItem;
    },

    observer: function () {
        var solicitationitem = this.solicitationitem();

        if (solicitationitem) {

            this.getControlPanel().enable();

            this.getComplementaryDescriptionAddedGrid().enable();
            this.getComplementaryDescriptionAddedGrid().setParam('solicitation_item', solicitationitem);
            this.getComplementaryDescriptionAddedGrid().setFilterProperty('solicitation_item', solicitationitem, 100);

            this.displayMinuteSolicitationItemGrid().setFilterProperty('solicitation', this.values.solicitation, 0);
            this.displayMinuteSolicitationItemGrid().getStore().reload();

        } else {

            this.getControlPanel().disable();
            this.getComplementaryDescriptionAddedGrid().disable();
        }
    },

    getButtons: function (cfg) {

        if (!this._buttons) {
            this._buttons = [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            ];

            if (!cfg.disableSave)
                this._buttons = [{
                    text: 'Salvar',
                    scope: this,
                    tabIndex: 3,
                    handler: function () {
                        this.save(true);
                    },

                }].concat(this._buttons);


            if (cfg.action == 'create')
                this._buttons = [{
                    text: 'Novo',
                    scope: this,
                    handler: function () {
                        this.action = 'create';
                        this.getFormPanel().getForm().reset();
                        this.getSolicitationItem().getComboField().focus();
                        this.getComplementaryDescriptionGrid().getStore().removeAll();
                        this.getComplementaryDescriptionAddedGrid().getStore().removeAll();
                        this.getComplementaryDescriptionAddedGrid().disable();
                    },
                }].concat(this._buttons);

        }

        return this._buttons;
    },

    constructor: function (cfg) {

        cfg = cfg || {};

        Ext.applyIf(cfg, {

            saveAndContinue: {
                scope: this,
                fn: function (instance) {
                    this.solicitationitem(instance.pk);
                    this.oId = instance.pk;
                    this.action = 'update';
                }
            }

        });

        planning.hiring.minutesolicitation.MinuteSolicitationItemWindow.superclass.constructor.call(this, cfg);
        this.solicitationitem(cfg.oId === undefined ? null : cfg.oId);
    }
});

