Ext._define('raf.report.ExtractReportLocationPeriodWindow', {
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

        values.employee = 0;
        values.instance = 0;
        values.layout = 2;
        values.submetidos = 2;

        if (values.location == "" ) {
            values.validate = false;
            values.message = 'Informe a Lotação.';
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

    getLocationField: function() {

        if(!this._locationField) {
            this._locationField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Lotação",
                allowBlank: true,
                rest: "judicial.county.ExecutionOrganRestful",
                name: "location",
                disabled: false,
                preFilter: [
                    {property: 'pk__in', value: this.locationsFilter(), stage: 100},
                ],
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
                        title: 'Relatório consolidado por período e lotação.',
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
                          this.getLocationField()
                      ]
                  },
                  {
                      xtype:'fieldset',
                      title: '  Filtro  ',
                      collapsible: false,
                      disabled: false,
                      autoHeight:true,
                      items: [

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
                      xtype:'fieldset',
                      title: 'Observação',
                      collapsible: false,
                      autoHeight:true,
                      items: [
                          {
                              xtype: 'displayfield',
                              value: "*Remover Zeros: Suprime ou não os registros cujo quantitativo seja igual a zero.",
                              hideLabel: true,
                          },
                          {
                              xtype: 'displayfield',
                              value:"Quanto maior o período selecionado, maior o tempo necessário para o sistema gerar o relatório. " +
                                "Uma notificação no canto superior direito irá indicar quando o relatório estiver pronto.",
                              hideLabel: true,
                              style: {fontWeight: 'bold'},
                          }
                      ]
                  }
                ]
        });
        return this._formPanel;
    },

    locationsFilter: function(values) {
        if(values !== undefined)
            this._locationsFilter = values

        return this._locationsFilter;
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

        this.locationsFilter(
            (cfg.values.locationsFilter === undefined ? []: cfg.values.locationsFilter)
        );
        raf.report.ExtractReportLocationPeriodWindow.superclass.constructor.call(this, cfg);

    }
});
