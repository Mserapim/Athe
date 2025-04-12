Ext._define('rh.employee.specialized.tab.FunctionalDataFormPanel', {
    extend: 'rh.employee.specialized.tab.BaseTabPanel',

    rest: 'rh.employee.specialized.Restful',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        rh.employee.specialized.tab.FunctionalDataFormPanel.superclass.constructor.call(this, cfg);
    },

    getObjFieldFunctional: function(cfg){
        cfg = core.nullValue(cfg, {});
        if(!this._objFieldFunctional){
            Ext.applyIf(
                cfg,
                {
                    employeePk: cfg.employeePk,
                    employeeRegistry: cfg.employeeRegistry,
                    naturalPersonPk: cfg.naturalPersonPk,
                    organIdentifier: cfg.organIdentifier,
                    matriculaFieldBlocked: cfg.matriculaFieldBlocked, 
                    is_member: cfg.is_member

                }
            );
            this._objFieldFunctional = Ext._create('rh.employee.specialized.tab.fields.Functional', cfg);
        }
        return this._objFieldFunctional;
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
                    organIdentifier: cfg.organIdentifier,
                    matriculaFieldBlocked: cfg.matriculaFieldBlocked
                }
            );
            this._objField = Ext._create('rh.employee.specialized.tab.fields.FunctionalStatic', cfg);
        }
        return this._objField;
    },


    getItems: function(cfgPanel, cfg){
        cfg = core.nullValue(cfg, {});
        if(!this._items){
            var itemsfs = this.getObjField();
            var itemsf = this.getObjFieldFunctional(cfg);
            if(itemsf != undefined && itemsfs != undefined){
                this._items = itemsf.fields();
                this._items = this._items.concat([itemsfs.fields()])
            }
        }
        return this._items;
    },

});
