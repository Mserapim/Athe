Ext._define('rh.employee.specialized.tab.RawBasePanel', {
    extend: 'Ext.Panel',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                border: false
            }
        );
        rh.employee.specialized.tab.RawBasePanel.superclass.constructor.call(this, cfg);
        this.setManagerTab(cfg.managerTab);
    },

    setManagerTab: function(managerTab){
        this.managerTab = managerTab;
    },

    getManagerTab: function(){
        return this.managerTab;
    },
});
