
Ext._define('judicial.reports.LawsuitLogReportPanel', {
    extend: 'toolkit.widget.TabPanel',
    layout: {
        type: 'vbox',
        align: 'center'
    },

    constructor: function(params)
    {
        params = params || {};

        var cfg = Object.assign({
            title: 'Atuações em Procedimento',
            padding: 5,
            items: [this.getFormPanel()]
        }, params);

        judicial.reports.LawsuitLogReportPanel.superclass.constructor.call(this, cfg);
    },

    _getAutocomplete: function() {

        if(!this._autocomplete){
            this._autocomplete = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: "Procedimento",
                rest: "judicial.outcourtlawsuit.OutCourtLawsuitAdminRestful",
                name: "outcourtlawsuit",
                displayField: 'lawsuit_unicode'
            });
        }

        return this._autocomplete;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                title:'Relatório de Atuações em Procedimento',
                frame: true,
                margin:'50px 100px',
                width: '40%',
                autoHeight: true,
                items: [
                    this._getAutocomplete()
               ],
               buttons:[
                    {
                        xtype: 'button',
                        scope: this,
                        tooltip: 'Gerar relatório de Atuações em Procedimento',
                        text: 'Gerar relatório',
                        padding: '2px 5px',
                        handler: function(btn, event){
                            var value = this._getAutocomplete().getValue();

                            engine.mq.Report.request({
                                report: '/to/mpe/judicial/activity_report',
                                waitMessage: 'Gerando relatório...',
                                params: {
                                    report_name: 'Relatório de Atuações em Procedimento',
                                    outfile: 'relatorio-de-atuacoes-em-procedimento.pdf',
                                    outcourtlawsuit: value
                                }
                            });
                        }
                    }
                ]
            });

        return this._formPanel;
    },
});
