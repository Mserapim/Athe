Ext._define('rh.employee.specialized.tab.BaseTabPanel', {
    extend: 'rh.employee.specialized.tab.RawBasePanel',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        var managerTab = cfg.managerTab || -1;
        var employeePk = cfg.employeePk || -1;
        var employeeRegistry = cfg.employeeRegistry || -1;
        var naturalPersonPk = cfg.naturalPersonPk || -1;
        var organIdentifier = cfg.organIdentifier || '';
        var matriculaFieldBlocked = cfg.matriculaFieldBlocked || false;
        var is_member = cfg.is_member || false;

        Ext.applyIf(
            cfg,
            {
                frame: true,
                height: 650,
                autoScroll: true,
                items: this.getItems(
                    {},
                    {
                        managerTab: managerTab,
                        employeePk: employeePk,
                        employeeRegistry: employeeRegistry,
                        naturalPersonPk: naturalPersonPk,
                        organIdentifier: organIdentifier,
                        matriculaFieldBlocked: matriculaFieldBlocked,
                        is_member: is_member,
                    }
                )
            }
        );
        rh.employee.specialized.tab.BaseTabPanel.superclass.constructor.call(this, cfg);
        this.observe({
            employeePk: employeePk,
            employeeRegistry: employeeRegistry,
            naturalPersonPk: naturalPersonPk,
            organIdentifier: organIdentifier,
            matriculaFieldBlocked: matriculaFieldBlocked,
            is_member: is_member
        });
    },

    observe: function(cfg){
        cfg = cfg || {};
        var obj = this.getObjField();
        if(obj != undefined){
            obj.myParams('managerTab', cfg.managerTab);
            obj.myParams('employeePk', cfg.employeePk);
            obj.myParams('employeeRegistry', cfg.employeeRegistry);
            obj.myParams('naturalPersonPk', cfg.naturalPersonPk);
            obj.myParams('organIdentifier', cfg.organIdentifier);
            obj.myParams('matriculaFieldBlocked', cfg.matriculaFieldBlocked);
            obj.myParams('is_member', cfg.is_member);
        }
    },

    getItems: function(cfgPanel, cfg){
        cfg = core.nullValue(cfg, {});
        if(!this._items){
            this._items = this.getObjField(cfg);
            if(this._items != undefined)
                this._items = this._items.fields();
        }
        return this._items;
    },

    getObjField: function(cfg){
        this._objField = undefined;
        return this._objField;
    },
});
