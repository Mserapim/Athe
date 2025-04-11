
Ext._define('raf.management.DefineDate', {
    extend: 'core.RestfulWindow',

    getValues: function(c) {
        var values = this.getFormPanel().getForm().getValues();
        values.validate = true;
        return values;
    },

    getEmployeeField: function() {
        if(!this._employeeField) {
            this._employeeField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                hideLabel: true,
                allowBlank: true,
                rest: "raf.EmployeeRestful",
                name: "employee",
                disabled: false,
                preFilter: [
                    {property: 'tipo', value: 'M', stage: 100},
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

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                labelWidth: 75,
                border: false,
                items: [
                    {
                        xtype:'fieldset',
                        title: 'Definções do agendamento',
                        collapsible: false,
                        autoHeight:true,
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
                                        labelWidth: 75,
                                        columnWidth: 0.63,
                                        items: [
                                            {
                                                fieldLabel: 'Tipo de ação',
                                                xtype: 'combo',
                                                hiddenName: 'action_type',
                                                width: 150,
                                                value: 1,
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
                                                name: 'generic_date',
                                            },
                                        ]
                                    },
                                ]
                            },
                        ]
                    },
                    {
                        xtype:'fieldset',
                        title: 'Membro',
                        collapsible: false,
                        autoHeight:true,
                        items: [
                            this.getEmployeeField(),
                        ]
                    },
                ]
        });
        return this._formPanel;
    },

    agendar: function(cfg) {
        var values = this.getValues(cfg);
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Agendamento ação no(s) RAF(s)...'});
        if (values.validate) {
            mask.show();
            Ext.Ajax.request({
                scope: this,
                url: core.callAction('RAFFunctionalActivityReport', 'defineDate'),
                callback: function() {
                    cfg.values.rafGrid.getStore().reload();
                    mask.hide();
                },
                success: function(request) {
                    var rst = Ext.decode(request.responseText);
                    Ext.Msg.show({
                        title: 'Agendamento de ações do RAF',
                        msg: rst.message,
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK
                    });
                    this.close();
                    core.invokeCallback((this.callback || {}).success);
                },
                failure: function(request) {
                    var rst = Ext.decode(request.responseText);
                    Ext.Msg.show({
                        title: 'Agendamento de ações do RAF',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                },
                params: {
                    action_type: values.action_type,
                    generic_date: values.generic_date,
                    month: cfg.values.month,
                    year: cfg.values.year,
                    employee: values.employee
                },
            });
        } else {
            Ext.Msg.show({
              title: 'Agendamento de ações do RAF',
              msg: values.message,
              icon: Ext.Msg.ERROR,
              buttons: Ext.Msg.OK
            });
        }
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Agendar',
                    scope: this,
                    handler: function() { this.agendar(cfg); }
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
                title: 'Agendamento de ações do RAF',
                modal: true,
                resizable: false,
                border: false,
                width: 450,
            }
        );
        Ext.apply(
            cfg,
            {
                items: this.getFormPanel(),
                buttons: this.getButtons(cfg),
            }
        );
        raf.management.DefineDate.superclass.constructor.call(this, cfg);
    }
});
