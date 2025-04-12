/*****************************************************************************
*                                                                            *
*                              FOLHA DE PONTO                                *
*                                                                            *
*****************************************************************************/
Ext._define('rh.gfp.reports.employee.forms.TimeSheet', {
    extend: 'rh.gfp.reports.employee.forms.BaseForm',

    mixins: { '1': 'engine.mq.OutputFormatReportMixin' },

    generateReport: function() {  // mixin
        this.validateFields();

        engine.mq.Report.request({
            report: this.reportPath,
            params: this.getParams(),
            el: this.ownerCt.getEl() || this.getEl(),
            waitMessage: 'Processando...',
            showSuccessMsg: false,
        }, this.outputFormat());
    },

    _getYearStore: function (cfg) {
        var years = [];
        var date = new Date();

        date.setMonth(date.getMonth() + 1);

        for (var year = date.getYear() + 1900; year > date.getYear() + 1900 - 5; year--) {
            years.push([year, year])
        }

        return years;
    },

    getYearField: function (cfg) {
        if (this._yearField) {
            return this._yearField;
        }

        this._yearField = Ext._create('Ext.form.ComboBox', {
            fieldLabel: 'Ano',
            hiddenName: 'ano',
            store: this._getYearStore(),
            mode: 'local',
            triggerAction: 'all',
            editable: false,
            anchor: '99%',
            allowBlank: false,
        });

        return this._yearField;
    },

    getMonthField: function (cfg) {
        if (this._monthField) {
            return this._monthField;
        }

        this._monthField = Ext._create('Ext.form.ComboBox', {
            fieldLabel: 'Mês',
            hiddenName: 'mes',
            store: [
                [1, 'JANEIRO'],
                [2, 'FEVEREIRO'],
                [3, 'MARÇO'],
                [4, 'ABRIL'],
                [5, 'MAIO'],
                [6, 'JUNHO'],
                [7, 'JULHO'],
                [8, 'AGOSTO'],
                [9, 'SETEMBRO'],
                [10, 'OUTUBRO'],
                [11, 'NOVEMBRO'],
                [12, 'DEZEMBRO'],
            ],
            mode: 'local',
            triggerAction: 'all',
            editable: false,
            anchor: '99%',
            allowBlank: false,
        });

        return this._monthField;
    },


    /*****************************************************************************
    *                     PROPRIEDADES E MÉTODOS SOBRESCRITOS                    *
    *****************************************************************************/

    reportPath: '/to/mpe/rh/ponto/main',

    onFetchEmployeeSuccess: function (data) {
        if (this.getEmployeeType() === 'E') {
            this.reportPath = '/to/mpe/rh/ponto/main_estagiario';
        }
    },

    getReportName: function (cfg) {
        return 'Folha de Ponto';
    },

    getReportFilename: function (cfg) {
        return `folha-de-ponto-${this.slugify(this.getEmployeeName())}`;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.apply(cfg, {
            border: false,
            labelWidth: 33,
            items: [
                this.getEmployeeHiddenField(cfg),
                this.getYearField(cfg),
                this.getMonthField(cfg),
            ],
            buttonAlign: 'left',
            buttons: [ this.getRunReportButton() ],  // mixin
        });

        rh.gfp
          .reports
          .employee
          .forms
          .TimeSheet
          .superclass
          .constructor
          .call(this, cfg);
    },
});
