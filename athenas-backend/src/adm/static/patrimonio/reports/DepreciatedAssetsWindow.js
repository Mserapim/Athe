Ext._define('adm.patrimonio.reports.DepreciatedAssetsWindow', {
    extend: 'adm.patrimonio.reports.GenericReportWindow',

    _report: '/to/mpe/adm/patrimonio/Contabil_de_Bens_Depreciado',

    _reportName: ' de Bens Depreciados',

    getFormItems: function(cfg) {
        return [
            this.getReportTypeField(cfg),
            this.getInitialDateField(cfg),
            this.getFinalDateField(cfg),
            this.getDepartmentField(cfg),
            this.getDepreciatedField(cfg)
        ];
    },

    constructor: function(cfg) {
        cfg = cfg || {};
        adm.patrimonio.reports.DepreciatedAssetsWindow.superclass.constructor.call(this, cfg);
    }
});
