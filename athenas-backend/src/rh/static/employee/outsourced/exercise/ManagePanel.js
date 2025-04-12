/**
 *
 **/

Ext._define('rh.employee.outsourced.exercise.ManagePanel', {
    extend: 'rh.employee.workplace.managerbyemployee.ManagePanel',


    getEmployeeGrid: function (cfg_window, cfg) {
        if (!this._employeeGrid) {
            cfg = core.nullValue(cfg, {});
            Ext.apply(
                cfg,
                {
                    gridAutoLoad: true,
                    situationMenuValue: [
                        {
                            name: 'active',
                            checked: true,
                            value: true,
                        },
                        {
                            name: 'finished',
                            checked: true,
                            value: false,
                        },
                    ],
                        typePossessionItems: [
                            {
                                name: 'outsourced',
                                checked: true,
                                value: 'TCR',
                            },
                        ],
                    title: 'Terceirizado',
                    grid_name: 'rh.employee.outsourced.Grid',
                    hideItemsToolbar: ['add', 'edit', 'remove'],
                }
            );
            this._employeeGrid = rh.employee.outsourced.exercise.ManagePanel.superclass.getEmployeeGrid.call(this,cfg_window, cfg);
        }

        return this._employeeGrid;
    },

});
