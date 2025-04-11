Ext._define('planning.hiring.agreement.ReportAgreeBalance', {
    extend: 'planning.hiring.agreement.ReportWindowBase',

    title: 'Saldo Contrato',

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
                fieldLabel: "Contrato",
                name: "contrato",
                xtype: "rest-autocompletefield",
                rest: "planning.hiring.agreement.Restful"
            },
            {
                width: 200,
                allowBlank: true,
                fieldLabel: "Contratado",
                name: "fornecedor",
                xtype: "rest-autocompletefield",
                rest: "rh.pessoa.Restful"
            },
            {
                width: 200,
                allowBlank: false,
                fieldLabel: 'Início',
                name: 'data_inicio',
                xtype: 'datefield',
            },
            {
                width: 200,
                allowBlank: false,
                fieldLabel: 'Fim',
                name: 'data_final',
                xtype: 'datefield',
            },
            {
                xtype: 'choicefield',
                fieldLabel: 'Tipo Licitação',
                hiddenName: 'tipo_licitacao',
                choiceId: 'contrato.TIPO_LICITACAO',
                width: 200
            },
        ]
    },

    generate: function(preventClose) {
        var values = this.getFormPanel().getForm().getValues();

        values.contrato = values.contrato;
        values.contratado = values.contratado;
        if(values.data_inicio)
        {
            inicio_parts = values.data_inicio.split('/');
            values.data_inicio = inicio_parts[2]+'-'+inicio_parts[1]+'-'+inicio_parts[0];
        }
        if(values.data_final)
        {
            fim_parts = values.data_final.split('/');
            values.data_final = fim_parts[2]+'-'+fim_parts[1]+'-'+fim_parts[0];
        }
        values.tipo = values.tipo_licitacao;

        engine.mq.Report.request({
                report: '/to/mpe/planejamento/Objeto_Saldo_Contrato',
                el: this.getEl(),
                waitMessage: 'Gerando relatório...',
                params: Ext.apply(
                    values,
                    {
                        outfile: 'Saldo_por_Contrato_' + new Date().format("d/m/Y"),
                        report_name: 'Saldo por Contrato'
                    }
                ),
            });
        if(!preventClose) this.close();
    },
});
