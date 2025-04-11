Ext._define('engine.mq.Report', {
    extend: 'Object',

    singleton: {
        request: function(cfg, outputFormat) {
            outputFormat = outputFormat || 'PDF';

            Ext.applyIf(cfg, {
                report: undefined,
                params: {},
                reportBuilder: 'MQReportBuilder',
                el: Ext.getBody(),
                waitMessage: 'Processando...',
                showSuccessMsg: true,
            });

            Ext.applyIf(cfg.params, {
                outfile: 'relatorio',
                report_name: 'Relatório',
            });

            if (cfg.report === undefined) {
                throw new Error("engine.mq.Report: Parâmetro 'cfg.report' obrigatório.");
            }

            var mask = new Ext.LoadMask(cfg.el, {
                msg: cfg.waitMessage,
            });

            mask.show();
            Ext.Ajax.request({
                url: core.callAction(cfg.reportBuilder, 'start'),
                params: {
                    report: cfg.report,
                    params: Ext.encode(cfg.params),
                    output_format: outputFormat,
                },
                callback: function() {
                    mask.hide();
                },
                success: function(xhr) {
                    var result = Ext.decode(xhr.responseText);

                    if (!result.success) {
                        Ext.Msg.show({
                            title: 'Solicitando relatório',
                            msg: result.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    } else if (cfg.showSuccessMsg) {
                        Ext.Msg.show({
                            title: 'Solicitando relatório',
                            msg: result.message,
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK
                        });
                    }
                },
                failure: function() {
                    Ext.Msg.show({
                        title: 'Solicitando relatório',
                        msg: 'Recurso indisponível no momento.',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                },
            });
        }
    }

});


Ext._define('engine.mq.ReportWindow', {
    extend: 'Ext.Window',

    mixins: {
        '1': 'engine.mq.OutputFormatReportMixin'
    },

    width: 355,

    title: 'undefined',

    _filename: 'undefined',

    _reportName: 'undefined',

    _report: 'undefined',

    _waitMessage: 'Gerando relatório...',

    filename: function(params) {
        return this._filename;
    },

    reportName: function(params) {
        return this._reportName;
    },

    prepareDate: function(value, inFormat, outFormat) {
        return Ext.util.Format.date(
            Date.parseDate(value, (inFormat || 'd/m/Y')),
            (outFormat || 'Y-m-d')
        );
    },

    prepareValues: function(values) {
        return values;
    },

    generateReport: function(preventClose) {
        preventClose = core.nullValue(preventClose, false);

        if(!this.getFormPanel().getForm().isValid())
            return;

        var values = this.getFormPanel().getForm().getValues();
        var reportName = this.reportName(values);
        var filename = this.filename(values);

        values = this.prepareValues(values);

        engine.mq.Report.request(
            {
                report: this._report,
                params: Ext.apply(
                    values,
                    {
                        outfile: filename,
                        report_name: reportName
                    }
                ),
                el: this.getEl(),
                waitMessage: this._waitMessage,
            },
            this.outputFormat()
        );

        if(preventClose)
            this.getFormPanel().getForm().reset();
        else
            this.close();
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: []
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
                modal: true,
                border: false,
                items: [
                    this.getFormPanel(cfg)
                ],
                buttons: [
                    this.getRunReportButton(),
                    {
                        text: 'Limpar',
                        scope: this,
                        handler: function() { this.getFormPanel().getForm().reset();}
                    },
                    {
                        text: 'Fechar',
                        scope: this,
                        handler: function() { this.close(); }
                    }
                ]
            }
        );

        engine.mq.ReportWindow.superclass.constructor.call(this, cfg);
    }
});
