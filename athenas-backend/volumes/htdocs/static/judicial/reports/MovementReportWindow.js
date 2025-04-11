
Ext._define('judicial.reports.MovementReportWindow', {
    extend: 'judicial.reports.ReportBaseWindow',

    width: 850,

    _filename: 'relatorio-de-movimentacoes.pdf',

    _report: '/to/mpe/judicial/report_by_movement',

    _reportName: 'Relatório de Movimentações',

    getItemsFormPanel: function(cfg) {
    	var items = judicial.reports.MovementReportWindow.superclass.getItemsFormPanel.call(this, cfg);

    	items.push([
			 {
                xtype: "rest-autocompletefield",
                fieldLabel: "Movimento",
                rest: "judicial.params.GlosaryRestful",
                name: "legal_movement",
                displayField: 'title'
            },
            {
               xtype: "rest-autocompletefield",
               fieldLabel: "Taxonomia",
               rest: "judicial.taxonomy.LegalMovimentRestful",
               name: "taxonomy",
               displayField: 'path_cache'
           }
    	]);

    	return items;
    }
});
