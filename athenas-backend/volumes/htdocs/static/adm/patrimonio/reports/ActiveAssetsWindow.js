Ext._define('adm.patrimonio.reports.ActiveAssetsWindow', {
    extend: 'adm.patrimonio.reports.GenericReportWindow',

    getFormItems: function(cfg) {
        return [
            this.getAssetsField(cfg),
            this.getReportTypeField(cfg),
            this.getFinalDateField(cfg),
            this.getDepartmentField(cfg)
        ];
    },

    constructor: function(cfg) {
        cfg = cfg || {};
        adm.patrimonio.reports.ActiveAssetsWindow.superclass.constructor.call(this, cfg);
    }
});
