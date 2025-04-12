Ext._define('rh.ferias.holidayScale.HolidayScaleReportManager', {
    extend: 'toolkit.widget.TabPanel',

    mixins: {'1': 'engine.mq.OutputFormatReportMixin'},

    title: 'Apostila de Férias',

    _filename: 'escala_de_ferias',
    filename: function(type) {
        // return "".concat(this._filename, "-", {1: 'Analitico', 2 : 'Sintetico'}[type]);
        return "".concat(this._filename, " - ", 'analitico');
    },

    _reportName: 'Apostila de Férias',

    reportName: function() {
        return this._reportName;
    },

    report: '/to/mpe/rh/ferias/apostila_ferias',

    _waitMessage: '[[FF]] Gerando relatório...',


    // Campos do form
    getInitialDate: function() {
        if (!this._initialDate) {
            this._initialDate = Ext._create('Ext.form.DateField', {
                // anchor: '100%',
                fieldLabel: 'Início',
                name: 'dt_initial',
                maxValue: new Date(),
                // width: '300px',
                allowBlank: false
            });
        }

        return this._initialDate;
    },

    getFinalDate: function() {
        if (!this._endDate) {
            this._endDate = Ext._create('Ext.form.DateField', {
                // anchor: '100%',
                fieldLabel: 'Fim',
                name: 'dt_final',
                value: new Date(),
                maxValue: new Date(),
                allowBlank: false
            });
        }

        return this._endDate;
    },

    getAto: function() {
        if (!this._ato) {
            this._ato = Ext._create('Ext.form.TextField', {
                // anchor: '100%',
                fieldLabel: 'Ato',
                name: 'ato',
                width: '300px',
                allowBlank: false
            });
        }

        return this._ato;
    },

    generate: function(values) {
        engine.mq.Report.request({
            report: this.report,
            params: Ext.apply(
                values,
                {
                    outfile: this.filename(values.tipo),
                    report_name: this.reportName()
                }
            ),
            el: this.getEl(),
            waitMessage: 'Gerando relatório...',
        }, this.outputFormat());
    },

    // Formatando Valores
    formatValues: function() {
        var values = {
            success: true
        };
        try {
            try {

                var dt_inicial = this.getInitialDate().getValue();
                var dt_final = this.getFinalDate().getValue();

                if(!Date.parse(dt_inicial))
                    throw "Informe uma data inicial válida";
                else
                    values.dt_inicial = dt_inicial.format('Y-m-d');

                if(!Date.parse(dt_final))
                    throw "Informe uma data final válida";
                else
                    values.dt_final = dt_final.format('Y-m-d');

                values.ato = this.getAto().getValue();

                console.log("Valores do Form:",values);

            } catch(e) {
                values.success = false;
                values.msg = 'Erro ao Formatar valores, '+e;
                console.log('Error:', values)
            }
        } finally {
            return values;
        }
    },

    // Gerador do relatório
    generateReport: function() {
        var values = this.formatValues();

        if(values.success) {
            this.generate(values);
        } else {
            Ext.Msg.show({
                title: 'Validação',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: values.msg
            });
        }
    },


    getFormPanel: function(cfg) {
        if(!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                title: cfg.title,
                frame: true,
                width: 450,
                style: {
                    margin: '60px auto'
                },
                items: [
                    this.getAto(),
                    this.getInitialDate(),
                    this.getFinalDate(),
                ],
                buttons: [
                    this.getRunReportButton()
                ]
            });
        }

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        this._values = {};

        Ext.applyIf(cfg, {
            title: 'Relatório de Apostila de Férias',
        });

        Ext.apply(cfg, {
                items: this.getFormPanel(cfg),
            }
        );


        rh.ferias.holidayScale.HolidayScaleReportManager.superclass.constructor.call(this, cfg);
    }
});
