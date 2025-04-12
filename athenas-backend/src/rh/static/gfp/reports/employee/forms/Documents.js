/*****************************************************************************
*                                                                            *
*                               REQUERIMENTOS                                *
*                                                                            *
*****************************************************************************/
Ext._define('rh.gfp.reports.employee.forms.Documents', {
    extend: 'rh.gfp.reports.employee.forms.BaseForm',

    _reportName: 'unknown',

    _reportStore: [
        ['FÉRIAS', '/to/mpe/portalservidor/Ferias'],
        ['LICENÇA JUNTA MÉDICA', '/to/mpe/portalservidor/Licenca_Junta_Medica'],
        ['LICENÇA TRATAMENTO DE SAÚDE', '/to/mpe/portalservidor/Licenca_Tratamento_Saude'],
        ['REQUERIMENTO DE PROCURADOR', '/to/mpe/portalservidor/Requerimento_Procurador'],
        ['REQUERIMENTO DE PROMOTOR PROCURADOR', '/to/mpe/portalservidor/Requerimento_Promotor_Procurador'],
        ['REQUERIMENTO RESSARCIMENTO DESPESA', '/to/mpe/portalservidor/Requerimento_Ressarcimento_Despesa'],
        ['REQUERIMENTO INDENIZAÇÃO OFICIAL DE DILIGÊNCIAS', '/to/mpe/portalservidor/Requerimento_Indenizacao_Transporte_Oficial_Diligencias'],
        ['REQUERIMENTO SALÁRIO FAMÍLIA', '/to/mpe/portalservidor/Requerimento_Salario_Familia'],
        ['DECLARAÇÃO DE PARENTESCO', '/to/mpe/portalservidor/Declaracao_Parentesco'],
    ],

    getDocumentField: function (cfg) {
        if (this._documentField) {
            return this._documentField;
        }

        this._documentField = Ext._create('Ext.form.ComboBox', {
            fieldLabel: 'Documento',
            valueField: 'reportPath',
            displayField: 'reportName',
            editable: false,
            triggerAction: 'all',
            anchor: '99%',
            allowBlank: false,
            emptyText: 'Selecione um item...',
            submitValue: false,
            mode: 'local',
            store: Ext._create('Ext.data.ArrayStore', {
                fields: ['reportName', 'reportPath'],
                data: this._reportStore,
            }),
            listeners: {
                scope: this,
                select: function (combo, record, index) {
                    this._reportName = record.data.reportName;
                    this.reportPath = record.data.reportPath;
                },
            },
        });

        return this._documentField;
    },


    /*****************************************************************************
    *                     PROPRIEDADES E MÉTODOS SOBRESCRITOS                    *
    *****************************************************************************/

    reportPath: 'unknown',

    getReportName: function (cfg) {
        return this._reportName;
    },

    getReportFilename: function (cfg) {
        return `${this.slugify(this.getReportName(cfg))}-${this.slugify(this.getEmployeeName())}`;
    },

    generateButtonHandle: function (cfg) {
        this.validateFields(cfg);
        this.requestReport(cfg);
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.apply(cfg, {
            border: false,
            labelWidth: 70,
            items: [
                this.getEmployeeHiddenField(cfg),
                this.getDocumentField(cfg),
            ],
            buttonAlign: 'left',
            buttons: [ this.getGenerateButton(cfg) ],
        });

        rh.gfp
          .reports
          .employee
          .forms
          .Documents
          .superclass
          .constructor
          .call(this, cfg);
    },
});
