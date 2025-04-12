/**
 *
 **/
Ext._define('adm.patrimonio.reports.ActiveAssetsByLocationWindow', {
    extend: 'adm.patrimonio.reports.GenericReportWindow',

    prepareValues: function(values) {
        values.data_inicial = '1989-01-01';
        if (values.data_final)
            values.data_final = this.prepareDate(values.data_final);
        return values;
    },

    getFormItems: function(cfg) {
        return [
            cfg.fields.group ? this.getGrupoField(cfg) : {},
            cfg.fields.specie ? this.getEspecieField(cfg) : {},
            cfg.fields.location ? this.getLocationField(cfg) : {},
            this.getAccountField(cfg),
            this.getFinalDateField(cfg)
        ];
    },

    reportName: function(params) {
        return this._reportName;
    },

    getCustomTitle: function(cfg) {
        this.formattedReportName = (cfg._reportName || this._reportName);
        return this.formattedReportName;
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, { width: 450 });
        
        adm.patrimonio.reports.ActiveAssetsByLocationWindow.superclass.constructor.call(this, cfg);
    }
});
