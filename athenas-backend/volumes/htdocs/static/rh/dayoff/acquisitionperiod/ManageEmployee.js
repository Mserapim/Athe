Ext._define('rh.dayoff.acquisitionperiod.ManageEmployee', {
    extend: 'rh.dayoff.acquisitionperiod.Manage',

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
                title: 'Período Aquisitivo - Servidor'
            }
        );

        rh.dayoff.acquisitionperiod.ManageEmployee.superclass.constructor.call(this, cfg);
    },

    getToolbarItems: function () {
        return [
            this.getMenuItemBook(),
            this.getMenuItemChange(),
            this.getMenuItemConflicts(),
            this.getMenuItemBookOff()
        ];
    },

    openActivityWindow: function (actionCustom, title, type_window) {
        rh.dayoff.acquisitionperiod.ManageEmployee.superclass.openActivityWindow.call(this, actionCustom, title, 'employee');
    },

    getAcquisitionPeriodGrid: function (cfgManage, cfg) {
        cfg = core.nullValue(cfg, {});

        if (!this._grid) {
            Ext.apply(
                cfg,
                {
                    configOrderToolBar: ['-', 'sell', '-'],
                    hideItemsToolbar: ['remove', 'copy', 'edit', 'release', 'homologate'],
                    hiddenFilter: true,
                    doubleClickHandler: function () { console.info('Desabilitado.'); }
                }
            );
            this._grid = rh.dayoff.acquisitionperiod.ManageEmployee.superclass.getAcquisitionPeriodGrid.call(this, cfgManage, cfg);
        }
        return this._grid;
    },

    getActivityGrid: function (cfgManage, cfg) {
        if (!this._activityGrid) {
            Ext.apply(
                cfg,
                {
                    configOrderToolBar: ['detail', '-', '->', 'download'],
                }
            );
            this._activityGrid = rh.dayoff.acquisitionperiod.ManageAdmin.superclass.getActivityGrid.call(this, cfgManage, cfg);
        }
        return this._activityGrid;
    },
});
