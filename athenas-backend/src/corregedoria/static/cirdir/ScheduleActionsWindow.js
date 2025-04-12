
Ext._define('corregedoria.cirdir.ScheduleActionsWindow', {
    extend: 'core.RestfulWindow',

    storeYear: function(cfg) {
        if(!this._storeYear) {
            this._storeYear = Ext._create('Ext.data.Store', {
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('CIRDIRControlInformation', 'get_storeyear')
                    }),
                    baseParams: {
                    },
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            {type: "int", name: "key"},
                            {type: "str", name: "value"},
                        ]
                    })
                });
                storeYearCache = this._storeYear;
                this._storeYear.load({
                    scope: this,
                    callback: function() {

                    }
                });
            }
            return this._storeYear;
    },

    getEmployeeField: function() {
        if(!this._employeeField) {
            this._employeeField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: 'Pessoa',
                allowBlank: true,
                rest: "raf.EmployeeRestful",
                name: "employee",
                disabled: false,
                preFilter: [
                ],
                gridConfig: {
                    columnAction: false,
                    hideColumns: ['departure_unicode', 'effective_unicode', 'commission_unicode', 'elective_unicode', 'ativo'],
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                }
            });
        }
        return this._employeeField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                labelWidth: 60,
                border: false,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 30,
                                columnWidth: 0.63,
                                items: [
                                    {
                                        fieldLabel: 'Ação',
                                        xtype: 'combo',
                                        hiddenName: 'action_type',
                                        width: 185,
                                        value: 1,
                                        editable: false,
                                        triggerAction: 'all',
                                        store: [
                                            [1, ''],
                                            [2, 'ABERTURA'],
                                            [3, 'FECHAMENTO'],
                                        ],
                                    }
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 30,
                                columnWidth: 0.37,
                                items: [
                                    {
                                        xtype: 'datefield',
                                        fieldLabel: 'Data',
                                        name: 'action_date',
                                        width: 100,
                                    },
                                ]
                            },

                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 45,
                                columnWidth: 0.63,
                                items: [
                                    {
                                        fieldLabel: 'Critério',
                                        xtype: 'combo',
                                        hiddenName: 'criteria',
                                        width: 170,
                                        value: 1,
                                        editable: false,
                                        triggerAction: 'all',
                                        store: [
                                            [1, ''],
                                            [2, 'RESIDÊNCIA'],
                                            [3, 'DOCÊNCIA - 1º SEMESTRE'],
                                            [4, 'DOCÊNCIA - 2º SEMESTRE'],
                                            [5, 'BENS E DIREITOS'],
                                            [6, 'DÍVIDAS E ÔNUS REAIS'],
                                            [7, 'SAÚDE'],
                                            [8, 'DECLARAÇÃO DO IRPF'],
                                        ],
                                    }
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 25,
                                columnWidth: 0.37,
                                items: [
                                    {
                                        fieldLabel: 'Ano',
                                        xtype: 'combo',
                                        hiddenName: 'year',
                                        width: 105,
                                        editable: false,
                                        triggerAction: 'all',
                                        store: this.storeYear(cfg),
                                        valueField: 'key',
                                        displayField: 'value',
                                        allowBlank: true,
                                    }
                                ]
                            },
                        ]
                    },
                    this.getApplyTo(),
                    this.getEmployeeField()
                ]
        });
        return this._formPanel;
    },

    getApplyTo: function() {
        if(!this._groupApply) {
            this._groupApply = Ext._create('Ext.form.RadioGroup', {
                xtype: 'radiogroup',
                fieldLabel: 'Aplicar em',
                columns: 4,
                disabled: false,
                items: [
                    {boxLabel: 'Selecionar', name: 'apply_to', inputValue:'ONE', checked: true},
                    {boxLabel: 'Apenas Membros', name: 'apply_to', inputValue:'M'},
                    {boxLabel: 'Apenas Servidores', name: 'apply_to', inputValue:'S'},
                    {boxLabel: 'Todos', name: 'apply_to', inputValue:'ALL'}
                ],
                listeners: {
                    scope: this,
                    change: function(me, checked) {
                        this.getApplySelection(checked.inputValue)
                    }
                }
            });
        }
        return this._groupApply;
    },

    getApplySelection: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(!this._applySelection)
            this._applySelection = 'ONE';

        if(value !== undefined) {
            this._applySelection = value;

            if(dispatch) this.observerSelection();
        }

        return this._applySelection;
    },

    observerSelection: function() {
        var value = this.getApplySelection();

        if(value == 'ONE') {
            this.getEmployeeField().enable();
        } else {
            this.getEmployeeField().reset();
            this.getEmployeeField().disable();
        }

    },

    scheduleAction: function(cfg) {
        var values = this.getFormPanel().getForm().getValues();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Agendar ação...'});
        if (values) {
            mask.show();
            Ext.Ajax.request({
                scope: this,
                url: core.callAction('CIRDIRControlInformation', 'schedule_action'),
                callback: function() {
                    cfg.params.mainGrid.getStore().reload();
                    mask.hide();
                },
                success: function(request) {
                    var rst = Ext.decode(request.responseText);
                    Ext.Msg.show({
                        title: 'Agendar ação',
                        msg: rst.message,
                        icon: rst.success ? Ext.Msg.INFO : Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                    this.close();
                    core.invokeCallback((this.callback || {}).success);
                },
                failure: function(request) {
                    var rst = Ext.decode(request.responseText);
                    Ext.Msg.show({
                        title: 'Agendar ação',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                },
                params: values,
            });
        }
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                      text: 'Agendar',
                      scope: this,
                      handler: function() {
                        this.scheduleAction(cfg);
                      }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ];
        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                title: 'Agendar ação',
                modal: true,
                resizable: false,
                border: false,
                width: 600,
            }
        );
        Ext.apply(
            cfg,
            {
                items: this.getFormPanel(),
                buttons: this.getButtons(cfg),
            }
        );
        corregedoria.cirdir.ScheduleActionsWindow.superclass.constructor.call(this, cfg);
    }
});
