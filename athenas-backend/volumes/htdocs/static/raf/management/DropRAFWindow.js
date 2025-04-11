
Ext._define('raf.management.DropRAFWindow', {
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
        if (values.hasOwnProperty('ckd_activity') && values.ckd_activity == 'on') {
            values.activity = true;
        } else {
            values.activity = false;
        }
        if (values.hasOwnProperty('ckd_adjustment') && values.ckd_adjustment == 'on' ) {
            values.adjustment = true;
        } else {
            values.adjustment = false;
        }
        return values;
    },

    getEmployeeField: function() {
        if(!this._employeeField) {
            this._employeeField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: 'Membro',
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
                labelWidth: 50,
                border: false,
                items: [
                    {
                        xtype:'fieldset',
                        title: 'Parâmetros',
                        collapsible: false,
                        autoHeight:true,
                        labelWidth: 105,
                        items: [
                            {
                                xtype: 'textfield',
                                fieldLabel: 'Mês de Referência',
                                emptyText: 'mm/aaaa',
                                regex: /^(1[0-2]|0[1-9])\/(\d{4})$/,
                                regexText: 'Entrada inválida.<br/>Formato correto: <b>mm/aaaa</b>.',
                                maxLength: 7,
                                maxLengthText: 'Entrada inválida.<br/>Formato correto: <b>mm/aaaa</b>.',
                                name: 'raf_month',
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
                                                name: 'ckd_activity',
                                                boxLabel: 'Não excluir caso existam atividades registradas',
                                                checked: true,
                                            },
                                            {
                                                xtype: 'checkbox',
                                                name: 'ckd_adjustment',
                                                boxLabel: 'Não excluir caso existam solicitações de ajustes de atividades registradas',
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

    removerRAF: function() {
        var values = this.getValues();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Removendo RAFs...'});
        if (values.employee == '') {
            message = 'Tem certeza que deseja remover <b>TODOS</b> os RAFs do mês <b>'+values.month+'/'+values.year+'</b>?';
        }
        else {
            message = 'Tem certeza que deseja remover o RAF do mês <b>'+values.month+'/'+values.year+'</b>, para o membro:<br /><b>'+this.getEmployeeField().items.items["0"].lastSelectionText+'</b>?';
        }
        if (values.validate) {
            Ext.Msg.show({
                title: 'Remover RAF',
                msg: message,
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn=='no') return;
                    mask.show();
                    Ext.Ajax.request({
                        scope: this,
                        url: core.callAction('RAFFunctionalActivityReport', 'dropRAF'),
                        callback: function() {
                            mask.hide();
                        },
                        success: function(request) {
                            var rst = Ext.decode(request.responseText);
                            if (rst.success == true) {
                                Ext.Msg.show({
                                    title: 'Remover RAF',
                                    msg: rst.message,
                                    icon: Ext.Msg.INFO,
                                    buttons: Ext.Msg.OK
                                });
                                this.close();
                                core.invokeCallback((this.callback || {}).success);
                            } else {
                                Ext.Msg.show({
                                    title: 'Remover RAF',
                                    msg: rst.message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        },
                        failure: function(request) {
                            var rst = Ext.decode(request.responseText);
                            Ext.Msg.show({
                                title: 'Remover RAF',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        },
                        params: {
                            month: values.month,
                            year: values.year,
                            employee: values.employee,
                            activity: values.activity,
                            adjustment: values.adjustment,
                        },
                    });
                }
            });
        } else {
            Ext.Msg.show({
              title: 'Remover RAF',
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
                    text: 'Remover',
                    scope: this,
                    handler: function() { this.removerRAF(); }
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
                title: 'Remover RAF',
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
        raf.management.DropRAFWindow.superclass.constructor.call(this, cfg);
    }
});
