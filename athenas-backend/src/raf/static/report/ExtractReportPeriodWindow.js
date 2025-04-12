
Ext._define('raf.report.ExtractReportPeriodWindow', {
    extend: 'raf.report.BaseWindow',

    report_tabela: '/to/mpe/raf/espelho_consolidado_raf',
    report_listagem: '/to/mpe/raf/espelho_consolidado_lista_raf',

    _reportName: 'Extrato Consolidado',

    _filename: 'consolidado-raf',

    getValues: function() {
        var values = this.getFormPanel().getForm().getValues();
        var regex = /^(1[0-2]|0[1-9])\/(\d{4})$/;
        values.validate = true;
        if (regex.test(values.initial_raf)) {
            values.initial_year = values.initial_raf.split("/")[1];
            values.initial_month = values.initial_raf.split("/")[0];
            if (regex.test(values.final_raf)) {
              values.final_year = values.final_raf.split("/")[1];
              values.final_month = values.final_raf.split("/")[0];
            } else {
              values.validate = false;
              values.message = 'RAF FINAL incorreto.<br/>Formato correto: <b>mm/aaaa</b>.';
            }
        } else {
          values.validate = false;
          values.message = 'RAF INICIAL incorreto.<br/>Formato correto: <b>mm/aaaa</b>.';
        }
        if (values.employee == "" ) {
          values.employee = 0;
        }
        if (values.location == "" ) {
          values.location = 0;
        }

        return values;
    },

    generate: function(preventClose) {
        var values = this.getValues();
        if (values.validate) {
            engine.mq.Report.request({
                report: values.layout == 2 ? this.report_listagem : this.report_tabela,
                params: Ext.apply(
                    values,
                    {
                        outfile: this.filename()+(values.instance == 0 ? '' : (values.instance == 1 ? '-1instancia' : '-2instancia')),
                        report_name: this.reportName()
                    }
                ),
                el: this.getEl(),
                waitMessage: 'Gerando relatório...',
            });
            if(!preventClose) this.close();
        } else {
            Ext.Msg.show({
              title: 'Extrato Consolidado',
              msg: values.message,
              icon: Ext.Msg.ERROR,
              buttons: Ext.Msg.OK
            });
        }
    },

    getEmployeeField: function() {
        if(!this._employeeField) {
            this._employeeField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Membro",
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

    getLocationField: function() {
        if(!this._locationField) {
            this._locationField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Lotação",
                allowBlank: true,
                rest: "judicial.county.ExecutionOrganRestful",
                name: "location",
                disabled: false,
                gridConfig: {
                    columnAction: false,
                    hideColumns: ['habilita_protocolo', 'ativo', 'sigla', 'general_distribution', 'replacements', 'owner_unicode', 'employee_exercise_unicode'],
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download'],
                }
            });
        }

        return this._locationField;
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
                        title: '  Período  ',
                        collapsible: false,
                        autoHeight:true,
                        items: [
                          {
                            xtype: 'textfield',
                            fieldLabel: 'RAF Inicial',
                            emptyText: 'mm/aaaa',
                            regex: /^(1[0-2]|0[1-9])\/(\d{4})$/,
                            regexText: 'Entrada inválida.<br/>Formato correto: <b>mm/aaaa</b>.',
                            maxLength: 7,
                            maxLengthText: 'Entrada inválida.<br/>Formato correto: <b>mm/aaaa</b>.',
                            name: 'initial_raf',
                          },
                          {
                            xtype: 'textfield',
                            fieldLabel: 'RAF Final',
                            emptyText: 'mm/aaaa',
                            regex: /^(1[0-2]|0[1-9])\/(\d{4})$/,
                            regexText: 'Entrada inválida.<br />Formato correto: <b>mm/aaaa</b>.',
                            maxLength: 7,
                            maxLengthText: 'Entrada inválida.<br />Formato correto: <b>mm/aaaa</b>.',
                            name: 'final_raf',
                          },
                      ]
                    },
                    {
                        xtype:'fieldset',
                        title: '  Opções de agregação  ',
                        collapsible: false,
                        autoHeight:true,
                        items: [
                            {
                                xtype: 'choicefield',
                                fieldLabel: 'RAFs',
                                hiddenName: 'submetidos',
                                // width: 465,
                                choiceId: 'raf.REPORT_CONSOLIDADO_SUBMETIDO',
                            },
                            this.getEmployeeField(),
                            this.getLocationField(),
                            {
                                fieldLabel: 'Instância',
                                xtype: 'combo',
                                hiddenName: 'instance',
                                width: 200,
                                triggerAction: 'all',
                                editable: false,
                                store: [
                                    [0, 'TODAS AS INSTÂNCIAS'],
                                    [1, 'PRIMEIRA INSTÂNCIA'],
                                    [2, 'SEGUNDA INSTÂNCIA'],
                                ],
                            },
                      ]
                    },
                    {
                        xtype:'fieldset',
                        title: '  Opções de Layout  ',
                        collapsible: false,
                        disabled: false,
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
                                        labelWidth: 50,
                                        columnWidth: 0.5,
                                        items: [
                                            {
                                                fieldLabel: 'Layout',
                                                xtype: 'combo',
                                                id: 'layout',
                                                hiddenName: 'layout',
                                                width: 150,
                                                triggerAction: 'all',
                                                editable: false,
                                                store: [
                                                    [1, 'TABELA'],
                                                    [2, 'LISTAGEM'],
                                                ],
                                                listeners: {
                                                    scope: this,
                                                    select: function(index, scrollIntoView){
                                                        if (index.value==2) {
                                                            this.getFormPanel().getForm().findField('removezeros').enable();
                                                            this.getFormPanel().getForm().findField('subitemtype').enable();
                                                        } else {
                                                            this.getFormPanel().getForm().findField('removezeros').disable();
                                                            this.getFormPanel().getForm().findField('subitemtype').disable();
                                                        }
                                                    },
                                                    render: function(){
                                                        if (Ext.getCmp('layout').value!=2) {
                                                            this.getFormPanel().getForm().findField('removezeros').enable();
                                                            this.getFormPanel().getForm().findField('subitemtype').enable();
                                                        } else {
                                                            this.getFormPanel().getForm().findField('removezeros').disable();
                                                            this.getFormPanel().getForm().findField('subitemtype').disable();
                                                        }
                                                    },
                                                },
                                            },
                                        ],
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 90,
                                        columnWidth: 0.5,
                                        items: [
                                            {
                                                fieldLabel: 'Remover zeros',
                                                xtype: 'combo',
                                                id: 'removezeros',
                                                hiddenName: 'removezeros',
                                                width: 150,
                                                triggerAction: 'all',
                                                editable: false,
                                                store: [
                                                    [1, 'SIM'],
                                                    [2, 'NÃO'],
                                                ],
                                            },
                                        ]
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 50,
                                items: [
                                    {
                                        fieldLabel: 'Subitens',
                                        xtype: 'combo',
                                        id: 'subitemtype',
                                        hiddenName: 'subitemtype',
                                        width: 150,
                                        triggerAction: 'all',
                                        editable: false,
                                        store: [
                                            [0, 'Todos'],
                                            [1, 'Estatísticas/Quantidade'],
                                            [2, 'Movimentos'],
                                        ],
                                    },
                                ]
                            },
                        ]
                    },
                ]
        });
        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: this.reportName(),
                width: 700,
            }
        );

        Ext.apply(
            cfg,
            {

            }
        );

        raf.report.ExtractReportPeriodWindow.superclass.constructor.call(this, cfg);

    }
});
