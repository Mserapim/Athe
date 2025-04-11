/**
 *
 **/
Ext._define('rh.employee.workplace.managerbyworkplace.pendingexercises.Manage', {
    extend: 'rh.employee.workplace.managerbyworkplace.Manage',

    getGrid: function(cfg_window, cfg){
        cfg_window = core.nullValue(cfg_window, {});
        cfg = core.nullValue(cfg, {});
        if(!this._gridPendingExercises)
            this._gridPendingExercises = Ext._create('rh.employee.workplace.managerbyworkplace.pendingexercises.ManagePanel', cfg);
        return this._gridPendingExercises;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                layout: 'border',
                border: false,
                scope: this,
                items: this.getGrid(cfg, {}),
            }
        );
        rh.employee.workplace.managerbyworkplace.pendingexercises.Manage.superclass.constructor.call(this, cfg);
    }
});