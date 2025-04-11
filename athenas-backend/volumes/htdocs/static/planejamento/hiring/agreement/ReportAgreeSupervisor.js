Ext._define('planning.hiring.agreement.ReportAgreeSupervisor', {
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
                allowBlank: false,
                fieldLabel: 'Situação',
                hiddenName: 'agreement_status',
                xtype: 'combo',
                store: [
                    [1, 'TODOS'],
                    [2, 'SOMENTE ATIVOS'],
                    [3, 'SOMENTE INATIVOS'],
                ],
                allowBlank: false,
                triggerAction: 'all',
                mode: 'local'
            },
            {
                width: 200,
                allowBlank: false,
                fieldLabel: 'Tipo de Fiscal',
                hiddenName: 'agreementsupervisor_kind',
                xtype: 'combo',
                store: [
                    [1, 'TODOS'],
                    [2, 'SOMENTE TITULARES'],
                    [3, 'SOMENTE SUBSTITUTOS'],
                ],
                allowBlank: false,
                triggerAction: 'all',
                mode: 'local'
            },
        ]
    },

    generate: function(preventClose) {
        var values = this.getFormPanel().getForm().getValues();

        engine.mq.Report.request({
                report: '/to/mpe/planejamento/contrato/listagem_fiscais',
                el: this.getEl(),
                waitMessage: 'Gerando relatório...',
                params: Ext.apply(
                    values,
                    {
                        outfile: 'Listagem_de_Fiscais_de_Contratos_' + new Date().format("d/m/Y"),
                        report_name: 'Listagem de Fiscais de Contratos'
                    }
                ),
            });
        if(!preventClose) this.close();
    },
});
