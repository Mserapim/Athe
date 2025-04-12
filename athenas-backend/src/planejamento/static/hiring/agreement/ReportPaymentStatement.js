Ext._define('planning.hiring.agreement.ReportPaymentStatement', {
    extend: 'planning.hiring.agreement.ReportWindowBase',

    title: 'Extrato de Pagamento',

    getFormPanel: function(cfg_window, cfg) {
        if (!this._formPanel) {
            this._formPanel = planning.hiring.agreement.ReportPaymentStatement.superclass.getFormPanel.call(this, cfg_window, cfg);
            this._formPanel.insert(
                this._formPanel.items.length, {
                    width: 200,
                    allowBlank: true,
                    fieldLabel: "Número do Processo",
                    name: "numero",
                    xtype: "textfield",
                }
            );
            //            this._formPanel.insert(
            //                this._formPanel.items.length,
            //                {
            //                    width:200,
            //                    fieldLabel: 'Tipo',
            //                    hiddenName: 'tipo',
            //                    xtype: 'combo',
            //                    store: [
            //                        [1, 'Medições de Pagamentos'],
            //                        [2, 'Vigência do Contrato'],
            //                    ],
            //                    triggerAction: 'all'
            //                }
            //            );
        }
        return this._formPanel;
    },

    generate: function(preventClose) {
        var values = this.getFormPanel().getForm().getValues();

        values.contratado = values.pessoa;
        if (values.data_inicio) {
            inicio_parts = values.data_inicio.split('/');
            values.data_inicio = inicio_parts[2] + '-' + inicio_parts[1] + '-' + inicio_parts[0];
        }
        if (values.data_vencimento) {
            fim_parts = values.data_vencimento.split('/');
            values.data_final = fim_parts[2] + '-' + fim_parts[1] + '-' + fim_parts[0];
        }
        values.num_processo = values.numero;

        engine.mq.Report.request({
            report: '/to/mpe/planejamento/Extrato_Pagamento_por_Contrato',
            el: this.getEl(),
            waitMessage: 'Gerando relatório...',
            params: Ext.apply(
                values, {
                    outfile: 'Extrato_Pagamento_por_Contrato_' + new Date().format("d/m/Y"),
                    report_name: 'Extrato Pagamento por Contrato',
                }
            ),
        });
        if (!preventClose) this.close();
    },
});
