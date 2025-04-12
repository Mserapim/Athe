Ext._define('rh.reports.transparency.FormPanel', {
    extend: 'Ext.form.FormPanel',

    mixins: {
        '1': 'engine.mq.OutputFormatReportMixin'
    },

    getStoreYears: function(cfg, initialYear) {
        initialYear = initialYear || 2015;
        var currentYear = (new Date()).getFullYear();
        var store = [];
        for (var year=currentYear; year >= initialYear; year--)
            store.push([year.toString(), year.toString()]);
        return store;
    },

    getYearField: function(cfg) {
        if (!this.fields.year)
            this.fields.year = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'Ano',
                allowBlank: false,
                width: 180,
                triggerAction: 'all',
                editable: false,
                store: this.getStoreYears(),
                value: (new Date()).getFullYear().toString()
            });
        return this.fields.year;
    },

    getMonthField: function(cfg) {
        if (!this.fields.month)
            this.fields.month = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'Mês',
                allowBlank: false,
                width: 180,
                triggerAction: 'all',
                editable: false,
                store: [
                    ['1', 'JANEIRO'],
                    ['2', 'FEVEREIRO'],
                    ['3', 'MARÇO'],
                    ['4', 'ABRIL'],
                    ['5', 'MAIO'],
                    ['6', 'JUNHO'],
                    ['7', 'JULHO'],
                    ['8', 'AGOSTO'],
                    ['9', 'SETEMBRO'],
                    ['10', 'OUTUBRO'],
                    ['11', 'NOVEMBRO'],
                    ['12', 'DEZEMBRO'],
                    ['13', '13° SALÁRIO']
                ]
            });
        return this.fields.month;
    },

    getCategoryField: function(cfg) {
        if (!this.fields.category)
            this.fields.category = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'Categoria',
                allowBlank: false,
                width: 180,
                triggerAction: 'all',
                store: [
                    ['S', 'SERVIDORES'],
                    ['M', 'MEMBROS'],
                    ['P', 'PENSIONISTAS'],
                ],
                editable: false
            });
        return this.fields.category;
    },

    showError: function(title, msg) {
        Ext.Msg.show({
            title: title,
            msg: msg,
            buttons: Ext.Msg.OK,
            icon: Ext.Msg.ERROR
        });
    },

    doReportRequest: function(name, path, filename, params) {
        engine.mq.Report.request(
            {
                report: path,
                params: Ext.apply(
                    params,
                    {
                        outfile: filename,
                        report_name: name
                    }
                ),
                el: this.getEl(),
                waitMessage: this.waitMessage
            },
            this.outputFormat()
        );
    },

    validateReportParams: function(cfg) {
        if (!this.reportName || !this.reportPath)
            throw 'Ocorreu um erro durante a requisição do relatório. \
                Um ou mais parâmetros não foram passados corretamente \
                para geração do relatório. Por favor, contate a equipe de \
                desenvolvimento.';
    },

    validateFields: function() {
        if (!this.getForm().isValid())
            throw 'Por favor, preencha todos os campos.';
    },

    getReportParams: function(cfg) {
        var params = {};

        if (this.reportParams && this.reportParams.category)
            params.category = this.reportParams.category
        else
            params.category = this.getCategoryField().getValue();

        if (this.reportParams && this.reportParams.month)
            params.month = this.reportParams.month
        else
            params.month = this.getMonthField().getValue();

        if (this.reportParams && this.reportParams.year)
            params.year = this.reportParams.year
        else
            params.year = this.getYearField().getValue();

        if (!params.category || !params.year || !params.month)
            throw 'Ocorreu um erro durante a requisição do relatório. \
                Um ou mais parâmetros de relatório não estão sendo \
                passados corretamente. Por favor, contate a equipe de \
                desenvolvimento.';

        return params;
    },

    _replaceCharAt: function (originalString, index, replacement) {
        var substrBefore = originalString.substr(0, index);
        var substrAfter = originalString.substr(index + 1);
        return substrBefore + replacement + substrAfter;
    },
    
    _removeAccents: function (originalString) {
        var normalVowels = 'aaaaeeiooouAAAAEEIOOUcC';
        var accentedVowels = 'áàâãéêíóôõúÁÀÂÃÉÊÍÓÔÚçÇ';
    
        var newString = originalString.toString();
    
        for (var i = 0, index = -1; i < newString.length; i++) {
            index = accentedVowels.indexOf(newString[i]);
            if (index > -1)
                newString = this._replaceCharAt(newString, i, normalVowels[index]);
        }
        
        return newString;
    },

    _replaceAll: function (originalString, search, replacement) {
        return originalString.replace(new RegExp(search, 'g'), replacement);
    },

    getReportFileName: function(cfg) {
        var filename = this._removeAccents(this.getFormattedReportName());
        filename = filename.toLowerCase();
        filename = this._replaceAll(filename, ' ', '-');
        return filename;
    },

    getFormattedReportName: function(cfg) {
        var format = this.reportName;
        var category = this.getCategoryField().getValue();
        category = category === 'S' ? 'servidores' : 'membros';
        return format.replace('%s', category);
    },

    getReportPath: function(cfg) {
        return this.reportPath;
    },

    generateReport: function(preventClose) {
        try {
            this.validateReportParams();
            this.validateFields();
            this.doReportRequest(
                this.getFormattedReportName(),
                this.getReportPath(),
                this.getReportFileName(),
                this.getReportParams()
            );
        } catch(e) {
            this.showError('Erro', e);
        }
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        this.fields = {};

        var hideCategoryField = false;
        if (cfg.fieldsToHide)
            hideCategoryField = cfg.fieldsToHide.includes('category');

        Ext.apply(cfg, {
            border: false,
            layout: 'column',
            labelAlign: 'top',
            defaults: {
                border: false,
                columnWidth: 0.33,
                layout: 'form',
            },
            items: [
                hideCategoryField ? {} : {items: [this.getCategoryField(cfg)]},
                {
                    items: [this.getMonthField(cfg)]
                },
                {
                    items: [this.getYearField(cfg)]
                }
            ],
            buttons: [
                this.getRunReportButton()
            ],
            buttonAlign: 'center'
        });

        rh.reports.transparency.FormPanel.superclass.constructor.call(this, cfg);
    }
});
