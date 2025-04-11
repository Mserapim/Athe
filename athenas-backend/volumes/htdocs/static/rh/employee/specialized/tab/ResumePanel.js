Ext._define('rh.employee.specialized.tab.ResumePanel', {
    extend: 'rh.employee.specialized.tab.BaseTabPanel',

    rest: 'rh.employee.specialized.Restful',

    constructor: function(cfg) {
        rh.employee.specialized.tab.GraduationPanel.superclass.constructor.call(this, cfg);
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
            this._objField = Ext._create('rh.employee.specialized.tab.fields.Resume', cfg);
        }
        return this._objField;
    },
});
