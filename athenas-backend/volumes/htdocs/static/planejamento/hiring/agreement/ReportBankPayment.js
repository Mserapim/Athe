Ext._define('planning.hiring.agreement.ReportBankPayment', {
    extend: 'planning.hiring.agreement.ReportWindowBase',

    title: 'Pagamento por Contrato/OB',

    getFormPanel: function(cfg_window, cfg) {
        if(!this._formPanel){
            this._formPanel = planning.hiring.agreement.ReportBankPayment.superclass.getFormPanel.call(this, cfg_window, cfg);
            this._formPanel.insert(
                this._formPanel.items.length,
                {
                    width: 200,
                    allowBlank: true,
                    fieldLabel: "Número do Processo",
                    name: "numero",
                    xtype: "textfield",
                }
            );
        }
        return this._formPanel;
    },

    generate: function(preventClose) {
        var values = this.getFormPanel().getForm().getValues();

        values.contratado = values.pessoa;
        if(values.data_inicio)
        {
            inicio_parts = values.data_inicio.split('/');
            values.data_inicio = inicio_parts[2]+'-'+inicio_parts[1]+'-'+inicio_parts[0];
        }
        if(values.data_vencimento)
        {
            fim_parts = values.data_vencimento.split('/');
            values.data_final = fim_parts[2]+'-'+fim_parts[1]+'-'+fim_parts[0];
        }
        values.num_processo = values.numero;

        engine.mq.Report.request({
                report: '/to/mpe/planejamento/Listagem_de_Pagamentos_por_Contratos_e_Ordem_Bancaria',
                el: this.getEl(),
                waitMessage: 'Gerando relatório...',
                params: Ext.apply(
                    values,
                    {
                        outfile: 'Listagem_OB_Contrato_' + new Date().format("d/m/Y"),
                        report_name: 'Listagem de Pagamentos por Contrato e OB',
                    }
                ),
            });
        if(!preventClose) this.close();
    },
});
