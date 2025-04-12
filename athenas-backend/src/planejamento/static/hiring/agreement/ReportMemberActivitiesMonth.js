Ext._define('planning.hiring.agreement.ReportMemberActivitiesMonth', {
    extend: 'planning.hiring.agreement.ReportWindowBase',

    title: 'Relatório de exercícios em órgão de execução dos membros por mês',

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

    getRangeOfYears: function () {
        var years = [];
        for (var year = 2009; year <= new Date().getFullYear(); year++) {
            years.push([year, year]);
        }
        return years.reverse();
    },

    _getDocumentsFields: function(cfg) {
        return [
            {
                fieldLabel: 'Mês',
                xtype: 'combo',
                width: 200,
                hiddenName: 'mes',
                store: [
                    [1, 'JANEIRO'],
                    [2, 'FEVEREIRO'],
                    [3, 'MARÇO'],
                    [4, 'ABRIL'],
                    [5, 'MAIO'],
                    [6, 'JUNHO'],
                    [7, 'JULHO'],
                    [8, 'AGOSTO'],
                    [9, 'SETEMBRO'],
                    [10, 'OUTUBRO'],
                    [11, 'NOVEMBRO'],
                    [12, 'DEZEMBRO'],
                ],
                triggerAction: 'all',
                mode: 'local'
            },
            {
                width: 200,
                allowBlank: false,
                fieldLabel: 'Ano',
                name: 'ano',
                xtype: 'combo',
                store:  this.getRangeOfYears()
            },
            {
                width: 200,
                allowBlank: true,
                fieldLabel: "Membro",
                name: "membro",
                xtype: "rest-autocompletefield",
                rest: "rh.employee.Restful",
                preFilter: [
                    {'property':  'ativo', 'value': true, 'stage': 1}
                ]
            }
        ]
    },

    generate: function(preventClose) {
        var values = this.getFormPanel().getForm().getValues();

        engine.mq.Report.request({
                report: '/to/mpe/expediente/exercicios_membros_detalhado_meses',
                el: this.getEl(),
                waitMessage: 'Gerando relatório...',
                params: Ext.apply(
                    values,
                    {
                        outfile: 'relatorio_orgao_de_execucao' + new Date().format("d/m/Y"),
                        report_name: 'Relatório de exercícios em órgão de execução dos membros por mês'
                    }
                ),
            });
        if(!preventClose) this.close();
    },
});
