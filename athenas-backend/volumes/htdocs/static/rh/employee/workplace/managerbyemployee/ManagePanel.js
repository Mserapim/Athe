/**
 *
 **/

Ext._define('rh.employee.workplace.managerbyemployee.ManagePanel', {
    extend: 'Ext.Panel',

    getEmployeeGrid: function (cfg_window, cfg) {
        if (!this._employeeGrid) {
            cfg = core.nullValue(cfg, {});
            Ext.applyIf(
                cfg,
                {
                    title: 'Servidores',
                    grid_name: 'rh.employee.Grid',
                    rest: 'rh.employee.Restful',
                    region: 'north',
                    split: true,
                    minHeight: 200,
                    height: 250,
                    hideActions: ['edit', 'remove', 'copy'],
                    hideItemsToolbar: ['add', 'edit', 'remove'],
                    doubleClickHandler: function () { }
                }
            );
            this._employeeGrid = Ext._create(cfg.grid_name, cfg);

            this._employeeGrid.getSelectionModel().on({
                scope: this,
                rowselect: function (sm, index, record) {
                    this.employee(record.get('pk'));
                },
                rowdeselect: function (sm) {
                    this.employee(null);
                }
            });

            this._employeeGrid.getStore().on({
                scope: this,
                load: function () {
                    this.employee(null);
                }
            });

            this._employeeGrid.getStore().on({
                scope: this,
                load: function () {
                    var selected = (this._employeeGrid.getSelectionModel().getSelected());

                    if (selected)
                        this.employee(selected.get('pk'));
                    else
                        this.employee(null);
                }
            });
        }

        return this._employeeGrid;
    },

    employee: function (value, prevent) {
        prevent = core.nullValue(prevent, false);

        if (value !== undefined) {
            this._employee = value;

            this._workplace = undefined;
            this._possession = undefined;

            !prevent && this.observeEmployee();
        }

        return this._employee;
    },

    observeEmployee: function () {
        var value = this.employee();
        if (value != undefined) {
            this.getEmployeeWorkplaceGrid().enable();
            this.getEmployeeWorkplaceGrid().setParam('servidor', value);
            this.getEmployeeWorkplaceGrid().setFilterProperty('servidor__pk', value, 200);

            this.getWorkassignmentGrid().enable();
            this.getWorkassignmentGrid().setParam('servidor', value);
            var selected = this.getEmployeeGrid().getSelectionModel().getSelected()
            if (selected)
                this.getWorkassignmentGrid().setParam('type_by_possession', selected.json.type_by_possession);
            this.getWorkassignmentGrid().setFilterProperty('servidor__pk', value, 200);
        } else {
            var employee = this.getEmployeeWorkplaceGrid().getParams().servidor;
            if (employee != undefined) {
                this.getEmployeeWorkplaceGrid().disable();
                this.getEmployeeWorkplaceGrid().setParam('servidor', 0);
                this.getEmployeeWorkplaceGrid().setFilterProperty('servidor__pk', 0, 200, false);
                this.getEmployeeWorkplaceGrid().getStore().removeAll();

                this.getWorkassignmentGrid().disable();
                this.getWorkassignmentGrid().setParam('servidor', 0);
                this.getWorkassignmentGrid().setParam('child_of', undefined);
                this.getWorkassignmentGrid().setParam('lotacao', undefined);
                this.getWorkassignmentGrid().setParam('movimentacao_posse', undefined);
                this.getWorkassignmentGrid().setParam('type_by_possession', undefined);
                this.getWorkassignmentGrid().setFilterProperty('servidor__pk', 0, 200, false);
                this.getWorkassignmentGrid().removeFilterProperty('child_of', 300, false);
            }
        }
    },

    employeeWorkplace: function (record, prevent) {
        prevent = core.nullValue(prevent, false);
        if (record != undefined && record.get('pk') !== undefined) {
            this._employeeWorkplace = record.get('pk');
            this._workplace = record.get('lotacao');
            this._possession = record.get('movimentacao_posse');

            !prevent && this.observeWorkplace();
        }

        return this._employeeWorkplace;
    },

    observeWorkplace: function () {
        if (this._employeeWorkplace != undefined) {
            this.getWorkassignmentGrid().setParam('child_of', this._employeeWorkplace);
            this.getWorkassignmentGrid().setParam('lotacao', this._workplace);
            this.getWorkassignmentGrid().setParam('movimentacao_posse', this._possession);
            this.getWorkassignmentGrid().setFilterProperty('child_of', this._employeeWorkplace, 300);
        }
        else {
            this.getWorkassignmentGrid().setParam('child_of', undefined);
            this.getWorkassignmentGrid().setParam('lotacao', undefined);
            this.getWorkassignmentGrid().setParam('movimentacao_posse', undefined);
            if (this.getWorkassignmentGrid().getParams().child_of != undefined) {
                this.getWorkassignmentGrid().removeFilterProperty('child_of');
                this.getWorkassignmentGrid().getStore().reload();
            }
        }
    },

    getEmployeeWorkplaceGrid: function (cfg_window, cfg, gridClass) {
        if (!this._employeeWorkplaceGrid) {
            cfg = core.nullValue(cfg, {});
            Ext.applyIf(
                cfg,
                {
                    title: '. .  Titularidade',
                    region: 'center',
                    columnAction: false,
                    disabled: true,
                }
            );

            gridClass = gridClass == undefined ? 'rh.employee.workplace.managerbyemployee.WorkplaceGrid' : gridClass;
            this._employeeWorkplaceGrid = Ext._create(gridClass, cfg);

            this._employeeWorkplaceGrid.getSelectionModel().on({
                scope: this,
                rowselect: function (sm, index, record) {
                    this.employeeWorkplace(record);
                },
                rowdeselect: function (sm) {
                    this.employeeWorkplace(null);
                }
            });

            this._employeeWorkplaceGrid.getStore().on({
                scope: this,
                load: function () {
                    this.employeeWorkplace(null);
                }
            });

            this._employeeWorkplaceGrid.getStore().on({
                scope: this,
                load: function () {
                    var selected = (this._employeeWorkplaceGrid.getSelectionModel().getSelected());

                    if (selected) {
                        this.employeeWorkplace(selected);
                    } else {
                        this.employeeWorkplace(null);
                    }
                }
            });

            this._employeeWorkplaceGrid.setParam('designacao', false);
            this._employeeWorkplaceGrid.setFilterProperty('designacao', false, 1, false);
        }
        return this._employeeWorkplaceGrid;
    },

    getControlPanel: function () {
        if (!this._controlPanel)
            this._controlPanel = Ext._create('Ext.Panel', {
                width: 15,
                frame: true,
                layout: 'vbox',
                bodyStyle: {
                    'border-top': 0,
                    'border-bottom': 0
                },
            });
        return this._controlPanel;
    },

    getWorkassignmentGrid: function (cfg_window, cfg, gridClass) {
        if (!this._workassignmentGrid) {
            cfg = core.nullValue(cfg, {});
            Ext.applyIf(
                cfg,
                {
                    title: 'Designações de Exercício',
                    region: 'east',
                    split: true,
                    width: "50%",
                    columnAction: false,
                    disabled: true,
                }
            );

            gridClass = gridClass == undefined ? 'rh.employee.workplace.managerbyemployee.WorkassignmentGrid' : gridClass;
            this._workassignmentGrid = Ext._create(gridClass, cfg);

            this._workassignmentGrid.setParam('designacao', true);
            this._workassignmentGrid.setFilterProperty('designacao', true, 1, false);
        }
        return this._workassignmentGrid;
    },

    firstCall: function () {
        this.observeEmployee();
        this.observeWorkplace();
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                region: 'center',
                layout: 'border',
                border: false,
                scope: this,
                items: [
                    this.getEmployeeGrid(cfg, { departament: cfg.departament }),
                    {
                        region: 'center',
                        layout: 'border',
                        minHeight: 150,
                        scope: this,
                        bodyStyle: {
                            'border-left': 0,
                            'border-right': 0
                        },
                        layoutConfig: {
                            align: 'stretch'
                        },
                        items: [
                            this.getEmployeeWorkplaceGrid(cfg),
                            this.getControlPanel(),
                            this.getWorkassignmentGrid(cfg)
                        ]
                    }
                ],
                listeners: {
                    scope: this,
                    afterrender: function (owner) {
                        var grid = owner.getWorkassignmentGrid();
                        setTimeout(function () {
                            grid.enable();
                            grid.disable();
                        }, 100);
                    }
                }
            }
        );
        rh.employee.workplace.managerbyemployee.ManagePanel.superclass.constructor.call(this, cfg);
        this.firstCall();

        var grid = this.getWorkassignmentGrid();
        setTimeout(function () {
            grid.enable();
            grid.disable();
        }, 100);

    }
});
