Ext._define('rh.gfp.reports.employee.forms.BaseForm', {
    extend: 'Ext.form.FormPanel',

    reportPath: undefined,

    _employeeData: {
        name: 'unknown',
        id: 0,
        type: 'unknown',
        naturalPersonId: 0,
        storageDir: 'unknown',
    },

    getEmployeeName: function () {
        return this._employeeData.name;
    },

    getEmployeeId: function () {
        return this._employeeData.id;
    },

    getEmployeeType: function () {
        return this._employeeData.type;
    },

    getNaturalPersonId: function () {
        return this._employeeData.naturalPersonId;
    },

    getStorageDir: function () {
        return this._employeeData.storageDir;
    },

    fetchEmployee: function () {
        Ext.Ajax.request({
            url: core.callAction('GFPReportUsuario', 'employee'),
            scope: this,
            success: function (xhr) {
                var result = Ext.decode(xhr.responseText);

                if (!result.success) {
                    this.onFetchEmployeeFailure(result.message);
                    return;
                }

                this._employeeData.name = result.employee.name;
                this._employeeData.id = result.employee.id;
                this._employeeData.type = result.employee.type;
                this._employeeData.naturalPersonId = result.employee.naturalPersonId;
                this._employeeData.storageDir = result.employee.storageDir;
                this.getEmployeeHiddenField().setValue(result.employee.id);

                this.onFetchEmployeeSuccess(result.employee);
            },
            failure: function (xhr) {
                this.onFetchEmployeeFailure('Recurso indisponível no momento.');
            },
        });
    },

    getEmployeeHiddenField: function (cfg) {
        if (this._employeeField) {
            return this._employeeField;
        }

        this._employeeField = Ext._create('Ext.form.Hidden', {
            name: 'servidor',
            value: 0,
            allowBlank: false,
        });

        return this._employeeField;
    },

    slugify: function (str) {
        return str.toLowerCase().split(' ').join('-');
    },

    getDisplayByValue: function (args) {
        args = args || {
            store: undefined,
            valueField: undefined,
            value: undefined,
            displayField: undefined,
        };

        var query = args.store.query(
            args.valueField, new RegExp('^' + args.value + '$')
        );

        if (query.length <= 0) {
            return '';
        }

        return query.first().data[args.displayField];
    },

    validateFields: function (cfg) {
        if (this.getForm().isValid()) {
            return;
        }

        Ext.Msg.show({
            title: 'Validando',
            msg: 'Por favor, preencha os campos obrigatórios.',
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK,
        });

        throw new Error('Por favor, preencha os campos obrigatórios.');
    },

    requestReport: function(cfg) {
        engine.mq.Report.request({
            report: this.reportPath,
            params: this.getParams(cfg),
            el: this.ownerCt.getEl() || this.getEl(),
            waitMessage: 'Processando...',
            showSuccessMsg: false,
        }, 'PDF');
    },

    getGenerateButton: function(cfg) {
        if (this._generateButton) {
            return this._generateButton;
        }

        this._generateButton = Ext._create('Ext.Button', {
            text: 'Gerar',
            scope: this,
            iconCls: 'icon-ged icon-ged-application-pdf',
            handler: function () {
                this.generateButtonHandle(cfg);
            },
        });

        return this._generateButton;
    },


    /*****************************************************************************
    *      PROPRIEDADES E MÉTODOS COM MAIS CHANCES DE SEREM SOBRESCRITOS         *
    *****************************************************************************/

    onFetchEmployeeSuccess: function (data) {
        // Override me
    },

    onFetchEmployeeFailure: function (error) {
        throw new Error(`Ocorreu um erro ao requisitar informações do funcionário: ${error}`);
    },

    getReportName: function (cfg) {
        return 'Relatório';
    },

    getReportFilename: function (cfg) {
        return 'relatorio';
    },

    getParams: function (cfg) {
        var params = this.getForm().getValues();

        return Ext.apply(params, {
            outfile: this.getReportFilename(cfg),
            report_name: this.getReportName(cfg),
        });
    },

    generateButtonHandle: function (cfg) {
        this.requestReport(cfg);  // Override me
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        rh.gfp
          .reports
          .employee
          .forms
          .BaseForm
          .superclass
          .constructor
          .call(this, cfg);

        this.fetchEmployee();
    },
});
