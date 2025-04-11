
Ext._define('raf.management.DropEproc2AthenasWindow', {
    extend: 'core.RestfulWindow',

    getValues: function() {
        var values = this.getFormPanel().getForm().getValues();
        values.validate = true;
        var regex = /^(1[0-2]|0[1-9])\/(\d{4})$/;
        if (regex.test(values.raf_month)) {
            values.year = values.raf_month.split("/")[1];
            values.month = values.raf_month.split("/")[0];
        } else {
          values.validate = false;
          values.message = 'MÊS DE REFERÊNCIA incorreto.<br/>Formato correto: <b>mm/aaaa</b>.';
        }
        if (values.hasOwnProperty('ckd_processed') && values.ckd_processed == 'on') {
            values.processed = true;
        } else {
            values.processed = false;
        }
        return values;
    },

    getEmployeeField: function() {
        if(!this._employeeField) {
            this._employeeField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: 'Membro',
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
                labelWidth: 50,
                border: false,
                items: [
                    {
                        xtype:'fieldset',
                        title: 'Importação',
                        collapsible: false,
                        autoHeight:true,
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'column',
                                defaults: {
                                    labelAlign: 'left',
                                    style: 'margin-right: 15px;',
                                },
                                items: [
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 105,
                                        items: [
                                            {
                                                xtype: 'textfield',
                                                fieldLabel: 'Mês de referência',
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
                                        xtype:'panel',
                                        autoHeight:true,
                                        labelWidth: 55,
                                        layout: 'form',
                                        items: [
                                            {
                                                xtype: 'combobox',
                                                fieldLabel: 'Instância',
                                                hiddenName: 'instancia',
                                                width: 200,
                                                store: [
                                                    [0, 'TODAS AS INSTÂNCIAS'],
                                                    [1, '1ª INSTÂNCIA'],
                                                    [2, '2ª  INSTÂNCIA'],
                                                ],
                                                allowBlank: false,
                                                value: 0,
                                            },
                                        ]

                                    },
                                ]
                            },
                            {
                                xtype:'fieldset',
                                title: 'Controle',
                                collapsible: false,
                                autoHeight:true,
                                items: [
                                    {
                                        xtype:'panel',
                                        collapsible: false,
                                        autoHeight:true,
                                        labelWidth: 0,
                                        items: [
                                            {
                                                xtype: 'checkbox',
                                                name: 'ckd_processed',
                                                boxLabel: 'Não excluir caso existam documentos já processados.',
                                                checked: true,
                                            },
                                        ]
                                    },
                                ]
                            },
                        ]
                    },
                    {
                        xtype:'fieldset',
                        title: 'Opcional',
                        collapsible: false,
                        autoHeight:true,
                        items: [
                            this.getEmployeeField(),
                        ]
                    }
                ]
        });
        return this._formPanel;
    },

    excluir: function() {
        var values = this.getValues();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Removendo Documentos do e-Proc(s)...'});
        if (values.validate) {
            mask.show();
            Ext.Ajax.request({
                scope: this,
                url: core.callAction('RAFFunctionalActivityReport', 'dropEproc2AthenasRAF'),
                callback: function() {
                    mask.hide();
                },
                success: function(request) {
                    var rst = Ext.decode(request.responseText);
                    Ext.Msg.show({
                        title: 'Remover documento(s) do e-Proc',
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
                        title: 'Remover documento(s) do e-Proc',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                },
                params: {
                    month: values.month,
                    year: values.year,
                    instancia: values.instancia,
                    employee: values.employee,
                    processed: values.processed,
                },
            });
        } else {
            Ext.Msg.show({
              title: 'Remover documento(s) do e-Proc',
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
                    text: 'Excluir Documentos',
                    scope: this,
                    handler: function() { this.excluir(); }
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
                title: 'Remover documento(s) do e-Proc',
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
        raf.management.DropEproc2AthenasWindow.superclass.constructor.call(this, cfg);
    }
});
