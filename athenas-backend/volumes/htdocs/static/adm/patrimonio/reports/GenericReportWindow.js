Ext._define('adm.patrimonio.reports.GenericReportWindow', {
    
    extend: 'engine.mq.ReportWindow',

    //controller: undefined,

    mixins: {
        '1': 'engine.mq.OutputFormatReportMixin',
        '2': 'adm.patrimonio.reports.CommonFields'
    },

    formattedReportName: '',
    
    prepareValues: function(values) {
        var self = this;
        values = adm.patrimonio.reports.BaseWindow.superclass.prepareValues.call(this, values);
        
        ['data_inicial', 'data_final'].forEach(
            function(attr) {
                if (values[attr]) 
                    values[attr] = self.prepareDate(values[attr]);
            }
        );
        
        return values;
    },

    reportName: function(params) {
        var formattedName;
        var departments = ['Contabil', 'Patrimonial'];
        var reportsTypes = ['Sintetico', 'Analitico'];
        
        if (this.fields.reportTypeExtended)
            reportsTypes = ['', 'Analitico', 'Sintetico'];

        if (this.getReportTypeField().getValue() === 3)
            formattedName = 'Resumo {department} de Depreciacao';
        else {
            formattedName = '{department} {report_type}' + this._reportName;
            formattedName = formattedName.replace(
                '{report_type}',
                reportsTypes[this.getReportTypeField().getValue()]
            );
        }

        formattedName = formattedName.replace(
            '{department}',
            departments[this.getDepartmentField().getValue()]
        );

        this.formattedReportName = formattedName;
        return this.formattedReportName;
    },

    filename: function(params) {
        var filename = this.formattedReportName;

        function replaceAll(search, replacement) {
            return this.replace(new RegExp(search, 'g'), replacement);
        }
        String.prototype.replaceAll = replaceAll;

        filename = filename.toLowerCase();
        filename = filename.replaceAll(' ', '-');

        return filename;
    },

    getCustomTitle: function(cfg) {
        var departments = ['Contabil', 'Patrimonial'];

        var formattedName = '{department}' + (cfg._reportName || this._reportName);
        formattedName = formattedName.replace(
            '{department}',
            departments[cfg.fields.department]
        );

        return formattedName;
    },

    getFormItems: function(cfg) {
        return [];
    },

    getFormPanel: function(cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                labelWidth: 100,
                items: this.getFormItems(cfg)
            });
        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            resizable: true, 
            title: this.getCustomTitle(cfg),
        });

        adm.patrimonio.reports.GenericReportWindow.superclass.constructor.call(this, cfg);
    }
});
