/**
 *
 **/
Ext._define('auth.GroupManage', {
    extend: 'toolkit.widget.TabPanel',

    getGroupGrid: function(cfg) {
        if(!this._groupGrid)
            this._groupGrid = Ext._create('auth.GroupGrid', {
                region: 'center',
                autoPermissionsGroups: cfg.autoPermissionsGroups,
            });

        return this._groupGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Grupo de Usuário'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getGroupGrid(cfg)
                ]
            }
        );

        // this.callParent([cfg]);
        auth.GroupManage.superclass.constructor.call(this, cfg);
    }
});
