Ext._define('planning.hiring.agreement.ReportMonthReadjustment', {
    extend: 'planning.hiring.agreement.ReportWindowBase',

    title: 'Relatório contratos por mes de reajuste',

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
                fieldLabel: "Número de Contrato",
                name: "id",
                xtype: "rest-autocompletefield",
                rest: 'planning.hiring.agreement.Restful',
            },
            {
                width: 200,
                allowBlank: true,
                fieldLabel: 'Tipo de contrato',
                name: "tipo_contrato",
                choiceId: "contrato.TIPO_CONTRATO",
                xtype: "choicefield",
                hiddenName: "tipo_contrato",
                rest: 'planning.hiring.agreement.Restful'
            },
            {
                width: 200,
                allowBlank: true,
                fieldLabel: 'Situação',
                name: 'status',
                hiddenName: 'status',
                xtype: 'combo',
                store: [
                    [0, 'TODOS'],
                    [100, 'SOMENTE ATIVOS'],
                    [4, 'SOMENTE INATIVOS'],
                ],
                allowBlank: true,
                triggerAction: 'all',
                mode: 'local'
            },

            {
                width: 200,
                allowBlank: true,
                fieldLabel: "Mês de Referência",
                name: "mes",
                choiceId: "contrato.MES_REAJUSTE",
                xtype: "choicefield",
                hiddenName: "mes",
                rest: 'planning.hiring.agreement.Restful'
            },
            {
                width: 200,
                allowBlank: true,
                fieldLabel: 'Índice de Reajuste',
                name: "index",
                choiceId: "contrato.INDICE_REAJUSTE",
                xtype: "choicefield",
                hiddenName: "index",
                rest: 'planning.hiring.agreement.Restful'
            },
        ]
    },

    generate: function(preventClose) {
        var values = this.getFormPanel().getForm().getValues();

        if(values.id == ""){
            delete values.id
        }
        if(values.tipo_contrato == ""){
            delete values.tipo_contrato
        }
        if(values.status == ""){
            delete values.status
        }
        if(values.mes == ""){
            delete values.mes
        }
        if(values.index == ""){
            delete values.index
        }

        if(values.status == 0){
            delete values.status
        }

        engine.mq.Report.request({
                report: '/to/mpe/planejamento/contrato/reajuste',
                el: this.getEl(),
                waitMessage: 'Gerando relatório...',
                params: Ext.apply(
                    values,
                    {
                        outfile: 'Contratos_por_mes_de_reajuste_' + new Date().format("d/m/Y"),
                        report_name: 'Contratos por mês de reajuste',
                        _filename: 'relatorio-de-contratos-por-mes-reajuste.pdf',
                    }
                ),
            });
        if(!preventClose) this.close();
    },
});
