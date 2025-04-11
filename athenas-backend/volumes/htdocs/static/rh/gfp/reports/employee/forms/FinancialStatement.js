/*****************************************************************************
*                                                                            *
*                         RELATÓRIO FICHA FINANCEIRA                         *
*                                                                            *
*****************************************************************************/
Ext._define('rh.gfp.reports.employee.forms.FinancialStatement', {
    extend: 'rh.gfp.reports.employee.forms.BaseForm',

    getYearStore: function (cfg) {
        if (this._yearStore) {
            return this._yearStore;
        }

        this._yearStore =  Ext._create('Ext.data.JsonStore', {
            url: core.callAction('GFPReportUsuario', 'get_store/ano'),
            fields: ['codigo', 'descricao'],
            root: 'result',
            totalProperty: 'totalRows',
            autoLoad: true,
        });

        return this._yearStore;
    },

    getStartYearField: function (cfg) {
        if (this._startYearField) {
            return this._startYearField;
        }

        this._startYearField = Ext._create('Ext.form.ComboBox', {
            fieldLabel: 'Ano inicial',
            hiddenName: 'ano_inicial',
            valueField: 'codigo',
            displayField: 'descricao',
            editable: false,
            triggerAction: 'all',
            anchor: '99%',
            store: this.getYearStore(cfg),
        });

        return this._startYearField;
    },

    getEndYearField: function (cfg) {
        if (this._endYearField) {
            return this._endYearField;
        }

        this._endYearField = new Ext.form.ComboBox({
            fieldLabel: 'Ano final',
            hiddenName: 'ano_final',
            valueField: 'codigo',
            displayField: 'descricao',
            editable: false,
            triggerAction: 'all',
            anchor: '99%',
            store: this.getYearStore(cfg),
        });

        return this._endYearField;
    },


    /*****************************************************************************
    *                     PROPRIEDADES E MÉTODOS SOBRESCRITOS                    *
    *****************************************************************************/

    reportPath: '/to/mpe/gfp/financial_statement',

    getReportName: function (cfg) {
        var start = this.getStartYearField().getValue();
        var end = this.getEndYearField().getValue();
        return `Ficha Financeira ${start} a ${end}`;
    },

    getReportFilename: function (cfg) {
        var name = this.slugify(this.getEmployeeName());
        var start = this.getStartYearField().getValue();
        var end = this.getEndYearField().getValue();
        return `ficha-financeira-${name}-${start}-a-${end}`;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.apply(cfg, {
            border: false,
            labelWidth: 66,
            items: [
                this.getEmployeeHiddenField(cfg),  // mixin
                this.getStartYearField(cfg),
                this.getEndYearField(cfg),
            ],
            buttonAlign: 'left',
            buttons: [ this.getGenerateButton(cfg) ],  // mixin
        });

        rh.gfp
          .reports
          .employee
          .forms
          .FinancialStatement
          .superclass
          .constructor
          .call(this, cfg);
    },
});
