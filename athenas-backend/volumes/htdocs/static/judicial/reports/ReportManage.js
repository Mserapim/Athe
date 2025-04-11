Ext._define('judicial.reports.ReportManage', {
    extend: 'toolkit.widget.TabPanel',

    report: '/to/mpe/judicial/icp_tac',

    _reportName: 'Relatório para o Portal de Direitos Coletivos - CNMP',

    _filename: 'relatorio_portal_direitos_coletivos_CNMP',

    _defaultOutputFormat: 'CSV',

    mixins: {
        '1': 'engine.mq.OutputFormatReportMixin'
    },

    getListOutputFormat: function() {
        return [];
    },

    filename: function() {
        return this._filename;
    },

    reportName: function() {
        return this._reportName;
    },

    generate: function(values) {
        engine.mq.Report.request(
            {
                report: this.report,
                params: Ext.apply(
                    values,
                    {
                        outfile: this.filename(),
                        report_name: this.reportName()
                    }
                ),
                el: this.getEl(),
                waitMessage: 'Gerando relatório...',
            },
            this.outputFormat()
        );
    },

    formatValues: function() {
        var values = {
            success: true
        };
        
        return values;
    },

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

    getMain: function(cfg){
        if(!this._panel) {
            this._panel = Ext._create('Ext.Panel', {
                layout: 'border',
                region: 'center',
                height: 650,
                split: true,
                autoEl: {tag: 'center'},
                items: [
                    {
                        region: 'center',
                        border: false,
                        items: [
                            {
                                xtype: 'fieldset',
                                title: 'Relatório para o Portal de Direitos Coletivos - CNMP',
                                width: "33%",
                                style: 'margin: 5px',
                                align: 'center',
                                items: [
                                    this.getRunReportButton(cfg)
                                ]
                            },
                        ]
                    }
                ]
            });
            this.getRunReportButton().setIconClass('icon-ged icon-ged-text-plain');
        }
        return this._panel;
    },


    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Relatórios'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items:[
                    this.getMain(),
                ]
            }
        );

        judicial.reports.ReportManage.superclass.constructor.call(this, cfg);
    }
});
