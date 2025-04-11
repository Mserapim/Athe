Ext._define('planning.hiring.ride.ReportListMinuteAdhesion', {
    extend: 'planning.hiring.agreement.ReportWindowBase',

    title: 'Listagem de Adesões por Ata',

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
                fieldLabel: "Número da Ata",
                name: "ata",
                xtype: "rest-autocompletefield",
                rest: "planning.hiring.minute.MinuteRestful"
            },
            {
                width: 200,
                allowBlank: true,
                fieldLabel: "Solicitante",
                name: "solicitante",
                xtype: "rest-autocompletefield",
                rest: "rh.pessoa.Restful"
            },
            {
                xtype: "datefield",
                fieldLabel: "Data inicio",
                name: "data_inicio"
            },
            {
                xtype: "datefield",
                fieldLabel: "Data final",
                name: "data_final"
            },
        ]
    },

    generate: function(preventClose) {
        var values = this.getFormPanel().getForm().getValues();

        if(values.ata == ""){
            delete values.ata;
        }

        if(values.solicitante == ""){
            delete values.solicitante;
        }

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

        engine.mq.Report.request({
                report: '/to/mpe/planejamento/contrato/lista_adesoes_minuta',
                el: this.getEl(),
                waitMessage: 'Gerando relatório...',
                params: Ext.apply(
                    values,
                    {
                        outfile: 'lista_adesoes_minuta' + new Date().format("d/m/Y"),
                        report_name: 'Listagem de Adesões por Ata'
                    }
                ),
            });
        if(!preventClose) this.close();
    },
});
