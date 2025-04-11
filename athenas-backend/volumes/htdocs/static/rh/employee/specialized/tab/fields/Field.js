if(typeof(rh.employee.specialized.tab) == "undefined" || typeof(rh.employee.specialized.tab) == undefined){
    rh.employee.specialized.tab = {};
    rh.employee.specialized.tab.fields = {};
}

rh.employee.specialized.tab.fields.Field = function(cfg) {};

rh.employee.specialized.tab.fields.Field.prototype = {

    constructor: function(cfg) {
        cfg = cfg || {};
        this.myParams('employeePk', cfg.employeePk);
        this.myParams('employeeRegistry', cfg.employeeRegistry);
        this.myParams('naturalPersonPk', cfg.naturalPersonPk);
        this.myParams('managerTab', cfg.managerTab);
        this.myParams('is_member', cfg.is_member);
    },

    observerEmployeePk: function(){},

    observerEmployeeRegistry: function(){},

    observerNaturalPersonPk: function(){},

    observerManagerTab: function(){},

    myParams: function(key, value, prevent) {
        this.params = core.nullValue(this.params, {});
        prevent = core.nullValue(prevent, false);
        if(value !== undefined) {
            if(value == -1)
                value = undefined;

            if(this.params[key] == value)
                prevent = true;

            this.params[key] = value;

            if(!prevent){
                if(key == 'employeePk')
                    this.observerEmployeePk();
                else if(key == 'employeeRegistry')
                    this.observerEmployeeRegistry();
                else if(key == 'naturalPersonPk')
                    this.observerNaturalPersonPk();
                else if(key == 'managerTab')
                    this.observerManagerTab();
            }
        }
        return this.params[key];
    },

    updateEmployeePanel: function(mayChange){
        mayChange = mayChange || false;
        this.myParams('managerTab').getEmployeePanel().mayChangeTabNaturalPersonData(mayChange);
        this.myParams('managerTab').updateEmployeePanel(this.myParams('employeePk'));
    },

    _factoryGrid: function(Class, cfg){
        cfg = core.nullValue(cfg, {});

        Ext.apply(cfg, {servidor: this.myParams('employeePk')});
        Ext.applyIf(cfg, {height: 200, gridAutoLoad: false});

        var grid = Ext._create(Class, cfg);

        Ext.applyIf(
            grid,
            {
                scope: this,
                callBeforeExpand: function(){
                    var employee = this.scope.myParams('employeePk');
                    if(employee != undefined){
                        this.setParam('servidor', employee);
                        this.enable();
                        this.setFilterProperty('servidor__id', employee, 100);
                    }
                    else{
                        this.setParam('servidor', undefined);
                        this.disable();
                        this.removeFilterProperty('servidor__id', 100);
                    }
                }
            }
        );
        return grid;
    },

    _factoryFieldSet: function(cfg, grid){
        grid = core.nullValue(grid, {});
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            grid,
            {
                callBeforeExpand: function(){
                    console.info('_not_implemented');
                }
            }
        );
        Ext.applyIf(
            cfg,
            {
                height: 250,
                title: 'Não informado.',
                collapsible: true,
                collapsed: true,
                labelAlign: 'right',
                items:[],
                listeners: {
                    scope: this,
                    beforeexpand: function(panel, a) {
                        grid.callBeforeExpand();
                    },
                },
                scope: this,
            }
        );
        return Ext._create('Ext.form.FieldSet', cfg);
    },
};
