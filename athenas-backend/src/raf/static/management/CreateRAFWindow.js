
Ext._define('raf.management.CreateRAFWindow', {
    extend: 'core.RestfulWindow',

    getValues: function() {
        var values = this.getFormPanel().getForm().getValues();
        var regex = /^(1[0-2]|0[1-9])\/(\d{4})$/;
        values.validate = true;
        if (regex.test(values.raf_month)) {
            values.year = values.raf_month.split("/")[1];
            values.month = values.raf_month.split("/")[0];
        } else {
          values.validate = false;
          values.message = 'MÊS DE REFERÊNCIA incorreto.<br/>Formato correto: <b>mm/aaaa</b>.';
        }
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
                        title: 'Mês de Referência',
                        collapsible: false,
                        autoHeight:true,
                        items: [
                            {
                                xtype: 'textfield',
                                hideLabel: true,
                                emptyText: 'mm/aaaa',
                                regex: /^(1[0-2]|0[1-9])\/(\d{4})$/,
                                regexText: 'Entrada inválida.<br/>Formato correto: <b>mm/aaaa</b>.',
                                maxLength: 7,
                                maxLengthText: 'Entrada inválida.<br/>Formato correto: <b>mm/aaaa</b>.',
                                name: 'raf_month',
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

    gerarRAF: function() {
        var values = this.getValues();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Criando/Editando RAF(s)...'});
        if (values.validate) {
            mask.show();
            Ext.Ajax.request({
                scope: this,
                url: core.callAction('RAFFunctionalActivityReport', 'createRAF'),
                callback: function() {
                    this.managementGroupGrid.getStore().reload();
                    mask.hide();
                },
                success: function(request) {
                    var rst = Ext.decode(request.responseText);
                    Ext.Msg.show({
                        title: 'Gerar RAF',
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
                        title: 'Gerar RAF',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                },
                params: {
                    month: values.month,
                    year: values.year,
                    employee: values.employee
                },
            });
        } else {
            Ext.Msg.show({
              title: 'Gerar RAF',
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
                    text: 'Gerar',
                    scope: this,
                    handler: function() { this.gerarRAF(); }
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
                title: 'Criar/Editar RAF',
                modal: true,
                resizable: false,
                border: false,
                width: 700,
            }
        );
        Ext.apply(
            cfg,
            {
                items: this.getFormPanel(),
                buttons: this.getButtons(cfg),
            }
        );
        raf.management.CreateRAFWindow.superclass.constructor.call(this, cfg);
    }
});
