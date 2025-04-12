
Ext._define('raf.report.ExtractReportPeriodStatusRAF', {
    extend: 'raf.report.BaseWindow',

    report: '/to/mpe/raf/raf_status_entrega',

    _reportName: 'Status de Entrega do RAF',

    _filename: 'raf-status-entrega',

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
        if (values.mode == 1) {
            this._reportName = this._reportName + ' - SEM RAFs A SUBMETER';
            this._filename = this._filename + '-sem-rafs-a-submeter';
        }
        if (values.mode == 2) {
            this._reportName = this._reportName + ' - COM RAFs A SUBMETER';
            this._filename = this._filename + '-com-rafs-a-submeter';
        }
        if (values.validate) {
            engine.mq.Report.request({
                report: this.report,
                params: Ext.apply(
                    values,
                    {
                        outfile: this.filename(),
                        report_name: this.reportName()
                    }
                ),
                el: this.getEl(),
                waitMessage: 'Gerando relatório...',
            });
            if(!preventClose) this.close();
        } else {
            Ext.Msg.show({
              title: 'Status de Entrega do RAF',
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
                          {
                              fieldLabel: 'Filtro',
                              xtype: 'combo',
                              hiddenName: 'mode',
                              width: 270,
                              value: 0,
                              store: [
                                  [0, 'TODOS'],
                                  [1, 'SEM RAFs A SUBMETER'],
                                  [2, 'COM RAFs A SUBMETER'],
                              ],
                          }
                      ]
                    },
                    {
                        xtype:'fieldset',
                        title: '  Opções de Filtro  ',
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


        raf.report.ExtractReportPeriodStatusRAF.superclass.constructor.call(this, cfg);


    }
});
