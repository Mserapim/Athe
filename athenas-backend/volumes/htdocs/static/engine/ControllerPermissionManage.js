/**
 *
 **/
Ext._define('engine.ControllerPermissionManage', {
    extend: 'toolkit.widget.TabPanel',

    getControllerPermissionGrid: function(cfg) {
        if(!this._controllerPermissionGrid)
            this._controllerPermissionGrid = Ext._create('engine.ControllerPermissionGrid', {
                region: 'center',
                autoPermissionsFuncs: cfg.autoPermissionsFuncs,
            });

        return this._controllerPermissionGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Permissões de Funcionalidades'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getControllerPermissionGrid(cfg)
                ]
            }
        );

        // this.callParent([cfg]);
        engine.ControllerPermissionManage.superclass.constructor.call(this, cfg);
    }
});
