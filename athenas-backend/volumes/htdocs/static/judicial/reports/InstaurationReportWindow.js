
Ext._define('judicial.reports.InstaurationReportWindow', {
    extend: 'judicial.reports.ReportBaseWindow',

    width: 550,

    _filename: 'relatorio-de-instauracoes.pdf',

    _report: '/to/mpe/judicial/report_by_initiator',

    _reportName: 'Relatório de Instaurações',

    prepareValues: function(values) {
        values = judicial.reports.InstaurationReportWindow.superclass.prepareValues.call(this, values);
        values.instauration = 1;
        
        return values;
    }
});
