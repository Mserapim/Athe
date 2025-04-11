
Ext._define('corregedoria.inspection.report.HistoryInspectionReport', {
    extend: 'corregedoria.reportbuilder.BaseWindow',

    _report: '',

    // _list_output_format: [
    //   {
    //       title: 'Arquivo PDF',
    //       type: 'PDF',
    //       iconCls: 'icon-ged icon-ged-application-pdf'
    //   },
    //   {
    //       title: 'Arquivo CSV',
    //       type: 'CSV',
    //       iconCls: 'icon-ged icon-ged-text-plain',
    //   },
    // ],

    _reportName: 'Histórico de Inspeções',

    _filename: 'inspecoes-historico',

    _controller: 'INSPECTIONHistoryInspection',

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                labelWidth: 75,
                border: false,
                items: [
                    {
                        xtype:'fieldset',
                        title: 'Parâmetros',
                        collapsible: false,
                        autoHeight:true,
                        items: [
                          {
                            xtype: 'textfield',
                            fieldLabel: 'Início',
                            emptyText: 'mm/aaaa',
                            regex: /^(1[0-2]|0[1-9])\/(\d{4})$/,
                            regexText: 'Entrada inválida.<br/>Formato correto: <b>mm/aaaa</b>.',
                            maxLength: 7,
                            maxLengthText: 'Entrada inválida.<br/>Formato correto: <b>mm/aaaa</b>.',
                            name: 'initial',
                          },
                          {
                            xtype: 'textfield',
                            fieldLabel: 'Fim',
                            emptyText: 'mm/aaaa',
                            regex: /^(1[0-2]|0[1-9])\/(\d{4})$/,
                            regexText: 'Entrada inválida.<br/>Formato correto: <b>mm/aaaa</b>.',
                            maxLength: 7,
                            maxLengthText: 'Entrada inválida.<br/>Formato correto: <b>mm/aaaa</b>.',
                            name: 'final',
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
                title: 'Relatorio',
                width: 700,
            }
        );
        corregedoria.inspection.report.HistoryInspectionReport.superclass.constructor.call(this, cfg);
    }
});
