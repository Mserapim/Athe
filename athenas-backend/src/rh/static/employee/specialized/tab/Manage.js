Ext._define('rh.employee.specialized.tab.Manage', {
    extend: 'Ext.TabPanel',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
               title: '--------------------------------'
            }
        );

        var firstPanel = this.getSearchPanel({managerTab: this, departament: cfg.departament});
        var employeePanel = this.getEmployeePanel({}, {
            managerTab: this,
            departament: cfg.departament,
            organIdentifier: cfg.organIdentifier,
            matriculaFieldBlocked: cfg.matriculaFieldBlocked
        });

        Ext.apply(
            cfg,
            {
                activeTab: 1,
                region: 'center',
                border: false,
                items: [
                    firstPanel,
                    employeePanel
                ],
                listeners: {
                    scope: this,
                    beforetabchange: function(owner, newTab, currentTab){
                        if(newTab instanceof rh.employee.specialized.tab.EmployeePanel){
                            owner.getSearchPanel().getEmployeeSpecializedGrid().callUpdateEmployee(undefined, owner.getEmployeePanel().action);
                        }
                        owner.getEmployeePanel().changeActiveTabNaturalPersonData();
                        owner.doLayout();
                        owner.ownerCt.doLayout();
                    },
                }
            }
        );
        rh.employee.specialized.tab.Manage.superclass.constructor.call(this, cfg);

        firstPanel.setManagerTab(this);
        employeePanel.setManagerTab(this);

        var owner = this;
        setTimeout(function() {
            owner.setActiveTab(firstPanel);
        }, 1);

        this._setAction('search', firstPanel);
        this._setAction('update', employeePanel);
    },

    actions: function() {
        if(this._action == undefined){
            this._action = {
                create: undefined,
                update: undefined,
                search: undefined,
                newSearch: undefined,
                save: undefined,
            };
        }
        return this._action;
    },

    _setAction: function(action, method){
        if(this.actions()[action] == undefined)
            this.actions()[action] = method;
        return this.actions()[action];
    },

    _getAction: function(action, values){
        var method = {};
        values = values || {};
        if(action == 'create'){
            Ext.apply(values, {action: action});
            method = this._setAction(action, this.getEmployeePanel({}, values));
            method.updateEmployee(undefined, action);
        }
        else if(action == 'update'){
            Ext.apply(values, {action: action});
            method = this._setAction(action, this.getEmployeePanel({}, values));
            method.callReadData(values.oId, action);
        }
        else
            method = this._setAction(action);
        return method;
    },

    updateEmployeePanel: function(employeePk, action){
        action = action || 'update';
        this.getEmployeePanel().cpfExists(employeePk != undefined ? true : false);
        this.getEmployeePanel().callReadData(employeePk, action);
    },

    setTabPanel: function(cfg){
        cfg = core.nullValue(cfg, {});
        var tab = this._getAction(
            cfg.action,
            {
                oId: cfg.oId,
                employeePk: cfg.employeePk,
                employeeRegistry: cfg.employeeRegistry,
                naturalPersonPk: cfg.naturalPersonPk,
                managerTab: this
            }
        );
        tab.doLayout();
        this.setActiveTab(tab);
        this.doLayout();
    },

    getSearchPanel: function(cfg) {
        if(!this._searchPanel){
            cfg = core.nullValue(cfg, {});
            Ext.applyIf(
                cfg,
                {
                    title: 'Pesquisar',
                    department: cfg.department,
                    region: 'center'
                }
            );
            this._searchPanel = Ext._create('rh.employee.specialized.tab.SearchPanel', cfg);
        }
        return this._searchPanel;
    },

    getEmployeePanel: function(cfgManage, cfg) {
        cfg = core.nullValue(cfg, {});
        if(!this._employeePanel){
            Ext.applyIf(
                cfg,
                {
                    title: 'Cadastro',
                    region: 'center',
                    action: 'update',
                    values: 'remote',
                }
            );
            this._employeePanel = Ext._create('rh.employee.specialized.tab.EmployeePanel', cfg);
        }
        return this._employeePanel;
    },
});
