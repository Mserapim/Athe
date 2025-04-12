Ext._define('planning.hiring.meterage.ReportPayment', {
    extend: 'planning.hiring.agreement.ReportWindowBase',

    height: 220,

    title: 'Extrato de Pagamentos',

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 100,
                items: this._getDocumentsFields(cfg)
            });

        return this._formPanel;
    },

    _getDocumentsFields: function(cfg) {
        return [
            {
                width: 200,
                allowBlank: true,
                fieldLabel: 'Número do Processo',
                name: 'num_processo',
                xtype: 'textfield',
            },
            {
                width: 200,
                allowBlank: true,
                fieldLabel: 'Início',
                name: 'vencimento_inicio',
                xtype: 'datefield',
            },
            {
                width: 200,
                allowBlank: true,
                fieldLabel: 'Fim',
                name: 'vencimento_fim',
                xtype: 'datefield',
            },
            {
                width: 200,
                allowBlank: true,
                fieldLabel: "Contratado",
                name: "contratado",
                xtype: "rest-autocompletefield",
                rest: "rh.pessoa.Restful"
            }
        ];
    },

    generate: function(preventClose) {
        var values = this.getFormPanel().getForm().getValues();

        if(values.vencimento_inicio)
        {
            inicio_parts = values.vencimento_inicio.split('/');
            values.data_inicio = inicio_parts[2]+'-'+inicio_parts[1]+'-'+inicio_parts[0];
        }
        if(values.vencimento_fim)
        {
            fim_parts = values.vencimento_fim.split('/');
            values.data_final = fim_parts[2]+'-'+fim_parts[1]+'-'+fim_parts[0];
        }

        values.contratado = values.contratado;
        values.num_processo = values.num_processo;

        engine.mq.Report.request({
                report: '/to/mpe/planejamento/Extrato_Pagamento_por_Contrato',
                el: this.getEl(),
                waitMessage: 'Gerando relatório...',
                params: Ext.apply(
                    values,
                    {
                        outfile: 'extrato_pagamento_' + new Date().format("d/m/Y"),
                        report_name: 'Extrato de Pagamento por Contrato',
                    }
                ),
            });
        if(!preventClose) this.close();
    },
});
