
Ext._define('raf.report.ExtractAdjustmentWindow', {
    extend: 'raf.report.BaseWindow',

    report: '/to/mpe/raf/extrato_solicitacoes',

    _reportName: 'Extrato de Solicitações',

    _filename: 'produtividade-raf',

    getValues: function() {
        var values = this.getFormPanel().getForm().getValues();
        var regex = /^(1[0-2]|0[1-9])\/(\d{4})$/;
        values.validate = true;
        if (values.employee == "" ) {
          values.validate = false;
          values.message = 'Selecione um membro para geração do relatório.';
        } else {
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
                report: this.report,
                params: Ext.apply(
                    values,
                    {
                        outfile: this.filename()+'-'+values.employee,
                        report_name: this.reportName()+'-'+values.employee
                    }
                ),
                el: this.getEl(),
                waitMessage: 'Gerando relatório...',
            });

            if(!preventClose) this.close();
        } else {
            Ext.Msg.show({
              title: 'Extrato de Solcitações',
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
                          this.getEmployeeField(),
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


        raf.report.ExtractAdjustmentWindow.superclass.constructor.call(this, cfg);


    }
});
