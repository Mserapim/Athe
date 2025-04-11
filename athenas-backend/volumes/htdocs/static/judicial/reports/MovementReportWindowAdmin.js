
Ext._define('judicial.reports.MovementReportWindowAdmin', {
    extend: 'judicial.reports.ReportBaseWindow',

    width: 850,

    _filename: 'relatorio-de-movimentacoes.pdf',

    _report: '/to/mpe/judicial/report_by_movement_by_employee',

    _reportName: 'Relatório E-ext - Movimentações - Por Responsável',

    getItemsFormPanel: function(cfg) {
    	var items = judicial.reports.MovementReportWindowAdmin.superclass.getItemsFormPanel.call(this, cfg);

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
