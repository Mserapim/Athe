/**
 *
 **/

Ext._define('rh.employee.trainee.exercise.ManagePanel', {
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
                                name: 'trainee',
                                checked: true,
                                value: 'EST',
                            },
                        ],
                    title: 'Estagiario',
                    grid_name: 'rh.employee.trainee.Grid',
                    hideItemsToolbar: ['add', 'edit', 'remove'],
                }
            );
            this._employeeGrid = rh.employee.trainee.exercise.ManagePanel.superclass.getEmployeeGrid.call(this,cfg_window, cfg);
        }

        return this._employeeGrid;
    },









    // employee: function (value, prevent) {
    //     prevent = core.nullValue(prevent, false);

    //     if (value !== undefined) {
    //         this._employee = value;

    //         this._workplace = undefined;
    //         this._possession = undefined;

    //         !prevent && this.observeEmployee();
    //     }

    //     return this._employee;
    // },

    // observeEmployee: function () {
    //     var value = this.employee();


    //     if (value != undefined) {
    //         this.getEmployeeWorkplaceGrid().enable();
    //         this.getEmployeeWorkplaceGrid().setParam('servidor', value);
    //         this.getEmployeeWorkplaceGrid().setFilterProperty('servidor__pk', value, 200);

    //         this.getWorkassignmentGrid().enable();
    //         this.getWorkassignmentGrid().setParam('servidor', value);
    //         this.getWorkassignmentGrid().setFilterProperty('servidor__pk', value, 200);
    //     } else {
    //         var employee = this.getEmployeeWorkplaceGrid().getParams().servidor;

    //         console.log('value', employee);
    //         if (employee != undefined) {
    //             this.getEmployeeWorkplaceGrid().disable();
    //             this.getEmployeeWorkplaceGrid().setParam('servidor', 0);
    //             this.getEmployeeWorkplaceGrid().setFilterProperty('servidor__pk', 0, 200, false);
    //             this.getEmployeeWorkplaceGrid().getStore().removeAll();

    //             this.getWorkassignmentGrid().disable();
    //             this.getWorkassignmentGrid().setParam('servidor', 0);
    //             this.getWorkassignmentGrid().setParam('child_of', undefined);
    //             this.getWorkassignmentGrid().setParam('lotacao', undefined);
    //             this.getWorkassignmentGrid().setParam('movimentacao_posse', undefined);
    //             this.getWorkassignmentGrid().setFilterProperty('servidor__pk', 0, 200, false);
    //             this.getWorkassignmentGrid().removeFilterProperty('child_of', 300, false);
    //         }
    //     }
    // },

    // employeeWorkplace: function (record, prevent) {
    //     prevent = core.nullValue(prevent, false);
    //     if (record != undefined && record.get('pk') !== undefined) {
    //         this._employeeWorkplace = record.get('pk');
    //         this._workplace = record.get('lotacao');
    //         this._possession = record.get('movimentacao_posse');

    //         !prevent && this.observeWorkplace();
    //     }

    //     return this._employeeWorkplace;
    // },

    // observeWorkplace: function () {
    //     if (this._employeeWorkplace != undefined) {
    //         this.getWorkassignmentGrid().setParam('child_of', this._employeeWorkplace);
    //         this.getWorkassignmentGrid().setParam('lotacao', this._workplace);
    //         this.getWorkassignmentGrid().setParam('movimentacao_posse', this._possession);
    //         this.getWorkassignmentGrid().setFilterProperty('child_of', this._employeeWorkplace, 300);
    //     }
    //     else {
    //         this.getWorkassignmentGrid().setParam('child_of', undefined);
    //         this.getWorkassignmentGrid().setParam('lotacao', undefined);
    //         this.getWorkassignmentGrid().setParam('movimentacao_posse', undefined);
    //         if (this.getWorkassignmentGrid().getParams().child_of != undefined) {
    //             this.getWorkassignmentGrid().removeFilterProperty('child_of');
    //             this.getWorkassignmentGrid().getStore().reload();
    //         }
    //     }
    // },

    // getEmployeeWorkplaceGrid: function (cfg_window, cfg, gridClass) {
    //     if (!this._employeeWorkplaceGrid) {
    //         cfg = core.nullValue(cfg, {});
    //         Ext.applyIf(
    //             cfg,
    //             {
    //                 title: 'Lotações',
    //                 flex: 1.0,
    //                 border: false,
    //                 columnAction: false,
    //                 disabled: true,
    //             }
    //         );

    //         gridClass = gridClass == undefined ? 'rh.employee.workplace.managerbyemployee.WorkplaceGrid' : gridClass;
    //         this._employeeWorkplaceGrid = Ext._create(gridClass, cfg);

    //         this._employeeWorkplaceGrid.getSelectionModel().on({
    //             scope: this,
    //             rowselect: function (sm, index, record) {
    //                 this.employeeWorkplace(record);
    //             },
    //             rowdeselect: function (sm) {
    //                 this.employeeWorkplace(null);
    //             }
    //         });

    //         this._employeeWorkplaceGrid.getStore().on({
    //             scope: this,
    //             load: function () {
    //                 this.employeeWorkplace(null);
    //             }
    //         });

    //         this._employeeWorkplaceGrid.getStore().on({
    //             scope: this,
    //             load: function () {
    //                 var selected = (this._employeeWorkplaceGrid.getSelectionModel().getSelected());

    //                 if (selected) {
    //                     this.employeeWorkplace(selected);
    //                 } else {
    //                     this.employeeWorkplace(null);
    //                 }
    //             }
    //         });

    //         this._employeeWorkplaceGrid.setParam('designacao', false);
    //         this._employeeWorkplaceGrid.setFilterProperty('designacao', false, 1, false);
    //     }
    //     return this._employeeWorkplaceGrid;
    // },

    // getControlPanel: function () {
    //     if (!this._controlPanel)
    //         this._controlPanel = Ext._create('Ext.Panel', {
    //             width: 15,
    //             frame: true,
    //             layout: 'vbox',
    //             bodyStyle: {
    //                 'border-top': 0,
    //                 'border-bottom': 0
    //             },
    //         });
    //     return this._controlPanel;
    // },

    // getWorkassignmentGrid: function (cfg_window, cfg, gridClass) {
    //     if (!this._workassignmentGrid) {
    //         cfg = core.nullValue(cfg, {});
    //         Ext.applyIf(
    //             cfg,
    //             {
    //                 title: 'Designações de Exercício',
    //                 flex: 1.0,
    //                 border: false,
    //                 columnAction: false,
    //                 disabled: true,
    //             }
    //         );

    //         gridClass = gridClass == undefined ? 'rh.employee.workplace.managerbyemployee.WorkassignmentGrid' : gridClass;
    //         this._workassignmentGrid = Ext._create(gridClass, cfg);

    //         this._workassignmentGrid.setParam('designacao', true);
    //         this._workassignmentGrid.setFilterProperty('designacao', true, 1, false);
    //     }
    //     return this._workassignmentGrid;
    // },

    // firstCall: function () {
    //     this.observeEmployee();
    //     this.observeWorkplace();
    // },

    // s
});
