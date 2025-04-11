Ext._define('rh.employee.specialized.tab.ContactPanel', {
    extend: 'rh.employee.specialized.tab.BaseTabPanel',

    rest: 'rh.employee.specialized.Restful',

    constructor: function(cfg) {
        Ext.applyIf(cfg, {iconCls: 'icon-rh icon-core-contacts-tab',});
        rh.employee.specialized.tab.ContactPanel.superclass.constructor.call(this, cfg);
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
            this._objField = Ext._create('rh.employee.specialized.tab.fields.Contact', cfg);
        }
        return this._objField;
    },
});
