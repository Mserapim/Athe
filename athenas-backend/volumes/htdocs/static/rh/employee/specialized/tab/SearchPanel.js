Ext._define('rh.employee.specialized.tab.SearchPanel', {
    extend: 'rh.employee.specialized.tab.BasePanel',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                frame: true,
                layout: 'border',
                border: false,
                items:[
                    this.getEmployeeSpecializedGrid(cfg, {managerTab: cfg.managerTab, departament: cfg.departament})
                ],
            }
        );
        rh.employee.specialized.tab.SearchPanel.superclass.constructor.call(this, cfg);
    },

    setManagerTab: function(managerTab){
        rh.employee.specialized.tab.SearchPanel.superclass.setManagerTab.call(this, managerTab);
        this.getEmployeeSpecializedGrid().setManagerTab(this.getManagerTab());
    },

    getEmployeeSpecializedGrid: function(cfg_window, cfg){
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
                region: 'center',
                border: false,
                gridAutoLoad: false
        });
        if(!this._grid){
            this._grid = Ext._create('rh.employee.specialized.Grid', cfg);
            this._grid.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, record) {
                    this.getManagerTab().getEmployeePanel().action = 'update';
                },
                rowdeselect: function(sm) {}
            });
        }
        return this._grid;
    },
});
