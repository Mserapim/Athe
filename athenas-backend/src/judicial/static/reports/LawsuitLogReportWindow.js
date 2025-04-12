
Ext._define('judicial.reports.LawsuitLogReportWindow', {
    extend: 'judicial.reports.ReportBaseWindow',

    width: 550,

    _filename: 'relatorio-de-atuacoes-em-procedimento.pdf',

    _report: '/to/mpe/judicial/activity_report',

    _reportName: 'Relatório de Atuações em Procedimento',

    getItemsFormPanel: function(cfg) {
    	var items = [];
    	items.push([
			 {
                xtype: "rest-autocompletefield",
                fieldLabel: "Procedimento",
                rest: "judicial.outcourtlawsuit.OutCourtLawsuitAdminRestful",
                name: "outcourtlawsuit",
                displayField: 'lawsuit_unicode'
            }
    	]);

    	return items;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        judicial.reports.LawsuitLogReportWindow.superclass.constructor.call(this, cfg);

        if(cfg.lawsuit){
            this.on({
                afterrender: function(me) {
                    this.getFormPanel().getForm().setValues({'outcourtlawsuit': cfg.lawsuit.data.pk});
                }
            });
        }
    }

});
