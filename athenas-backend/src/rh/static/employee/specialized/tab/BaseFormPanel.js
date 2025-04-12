Ext._define('rh.employee.specialized.tab.BaseFormPanel', {
    extend: 'rh.employee.specialized.tab.BasePanel',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                frame: true,
                layout: 'form',
                border: false,
            }
        );
        rh.employee.specialized.tab.BaseFormPanel.superclass.constructor.call(this, cfg);
   },

});
