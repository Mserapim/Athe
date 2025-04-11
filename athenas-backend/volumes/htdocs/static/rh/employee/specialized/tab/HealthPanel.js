Ext._define('rh.employee.specialized.tab.HealthPanel', {
    extend: 'rh.employee.specialized.tab.BaseTabPanel',

    rest: 'rh.employee.specialized.Restful',

    constructor: function(cfg) {
        Ext.applyIf(cfg, {iconCls: 'icon-rh icon-core-health-tab',});
        rh.employee.specialized.tab.HealthPanel.superclass.constructor.call(this, cfg);
    },

    getObjField: function(cfg){
        cfg = core.nullValue(cfg, {});
        if(!this._objField){
            Ext.applyIf(
                cfg,
                {
                    employeePk: cfg.employeePk,
                    employeeRegistry: cfg.employeeRegistry,
                    naturalPersonPk: cfg.naturalPersonPk,
                }
            );
            this._objField = Ext._create('rh.employee.specialized.tab.fields.Health', cfg);
        }
        return this._objField;
    },
});
