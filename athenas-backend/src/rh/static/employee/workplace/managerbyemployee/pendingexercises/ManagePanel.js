/**
 *
 **/

Ext._define('rh.employee.workplace.managerbyemployee.pendingexercises.ManagePanel', {
    extend: 'rh.employee.workplace.managerbyemployee.ManagePanel',

    __title: 'Membros com exercícios pendentes',

    getEmployeeGrid: function (cfg_window, cfg) {
        if (!this._employeeGrid) {
            cfg = core.nullValue(cfg, {});
            Ext.applyIf(
                cfg,
                {
                    border: false,
                    grid_name: 'rh.employee.PendingExercisesGrid',
                    rest: 'rh.employee.PendingExercisesRestful'
                }
            );
            this._employeeGrid = rh.employee.workplace.managerbyemployee.pendingexercises.ManagePanel.superclass.getEmployeeGrid.call(
                this,
                cfg_window,
                cfg
            );

            this._employeeGrid.getStore().on({
                scope: this,
                load: function (store, records, opts) {
                    if (store.getTotalCount() > 0) {
                        this.setTitle(this.__title + ' (' + store.getTotalCount() + ')');
                        this.ownerCt.setTitle(this.__title + ' (' + store.getTotalCount() + ')');
                    } else {
                        this.setTitle(this.__title);
                        this.ownerCt.setTitle(this.__title);
                    }
                }
            });
        }

        return this._employeeGrid;
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});
        rh.employee.workplace.managerbyemployee.pendingexercises.ManagePanel.superclass.constructor.call(this, cfg);
    }
});
