Ext._define('adm.patrimonio.reports.AcquiredAssetsWindow', {
    extend: 'adm.patrimonio.reports.GenericReportWindow',

    getFormItems: function(cfg) {
        var acquisition = cfg.fields.acquisition;
        return [
            this.getAssetsField(cfg),
            this.getReportTypeField(cfg),
            acquisition ? this.getAcquisitionField(cfg) : this.getRetirementField(cfg),
            this.getInitialDateField(cfg),
            this.getFinalDateField(cfg),
            this.getDepartmentField(cfg),
        ];
    },

    constructor: function(cfg) {
        cfg = cfg || {};
        adm.patrimonio.reports.AcquiredAssetsWindow.superclass.constructor.call(this, cfg);
    }
});
