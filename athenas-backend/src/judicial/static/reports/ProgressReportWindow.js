
Ext._define('judicial.reports.ProgressReportWindow', {
    extend: 'judicial.reports.ReportBaseWindow',

    width: 550,

    _filename: 'relatorio-quantitativo-de-procedimentos-em-tramite.pdf',

    _report: '/to/mpe/judicial/report_by_progress',

    _reportName: 'Relatório - Quantitativo de procedimentos extrajudiciais em trâmite',

    prepareValues: function(values) {
        values = judicial.reports.ProgressReportWindow.superclass.prepareValues.call(this, values);
        
        values.detail = values.detail == 'on' ? true : false;
        return values;
    },

    getItemsFormPanel: function(cfg) {
        return [
            this.getWorkplaceField(cfg),
            {
                xtype: 'choicefield',
                emptyText: 'Todas as classes',
                withNone: true,
                withNoneLabel: 'Todas as classes',
                name: 'legal_class',
                hiddenName: 'legal_class',
                fieldLabel: 'Classe',
                width: 270,
                choiceId: 'judicial.TYPE_LAWSUIT'
            },
            {
                xtype: "rest-autocompletefield",
                fieldLabel: "Área de atuação",
                rest: "judicial.params.ActingZoneRestful",
                name: "acting_zone"
            },
            {
                xtype: "checkbox",
                boxLabel: "Listar procedimentos individualizados",
                allowBlank: true,
                name: "detail",
            },
        ];
    }
});
