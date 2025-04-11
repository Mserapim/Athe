Ext._define('rh.employee.specialized.tab.ProvisionPanel', {
    extend: 'rh.employee.specialized.tab.BaseTabPanel',

    rest: 'rh.employee.specialized.Restful',

    constructor: function(cfg) {
        rh.employee.specialized.tab.ProvisionPanel.superclass.constructor.call(this, cfg);
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
                    is_member: cfg.is_member,
                }
            );
            this._objField = Ext._create('rh.employee.specialized.tab.fields.Provision', cfg);
        }
        return this._objField;
    },
});
