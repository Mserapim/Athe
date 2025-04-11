Ext._define('planning.hiring.minutereport.MinuteExportXLS', {
    extend: 'planning.hiring.minutereport.BaseReportWindow',

    title: 'Exportação de Atas para XLS',

    _getDocumentsFields: function (cfg) {
        return [
            {
                columnWidth: '0.5',
                layout: 'form',
                items:
                {
                    width: 188,
                    allowBlank: false,
                    fieldLabel: 'Início',
                    name: 'expiration_from',
                    xtype: 'datefield',
                }
            },
            {
                columnWidth: '0.5',
                layout: 'form',
                items:
                {
                    width: 188,
                    allowBlank: false,
                    fieldLabel: 'Fim',
                    name: 'expiration_until',
                    xtype: 'datefield',
                }
            }
        ]
    },

    generate: function (preventClose) {
        var values = this.getFormPanel().getForm().getValues();

        if (values.expiration_from) {
            inicio_parts = values.expiration_from.split('/');
            values.expiration_from = inicio_parts[2] + '-' + inicio_parts[1] + '-' + inicio_parts[0];
        }

        if (values.expiration_until) {
            fim_parts = values.expiration_until.split('/');
            values.expiration_until = fim_parts[2] + '-' + fim_parts[1] + '-' + fim_parts[0];
        }

        engine.mq.Report.request({
            report: '/to/mpe/planejamento/export_minute_xls',
            el: this.getEl(),
            waitMessage: 'Gerando relatório...',
            params: Ext.apply(
                values,
                {
                    outfile: 'xls_minutes_' + new Date().format("d/m/Y"),
                    report_name: 'Atas de Registro de Preço - XLS',
                }
            ),
        }, 'XLS');

        if (!preventClose) this.close();
    },
});