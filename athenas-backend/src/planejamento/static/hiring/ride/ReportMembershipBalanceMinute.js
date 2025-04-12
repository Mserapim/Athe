Ext._define('planning.hiring.ride.ReportMembershipBalanceMinute', {
    extend: 'planning.hiring.agreement.ReportWindowBase',

    title: 'Saldo de Adesão',

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
                fieldLabel: "Ata",
                name: "ata",
                xtype: "rest-autocompletefield",
                rest: "rh.localidade.Restful"
            },
        ]
    },

    generate: function(preventClose) {
        var values = this.getFormPanel().getForm().getValues();

        if(values.ata == ""){
            delete values.ata;
        }

        engine.mq.Report.request({
                report: '/to/mpe/planejamento/contrato/saldo_adesao',
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
