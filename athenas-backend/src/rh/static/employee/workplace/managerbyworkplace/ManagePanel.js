/**
 *
 **/
 Ext._define('rh.employee.workplace.managerbyworkplace.ManagePanel', {
    extend: 'rh.employee.workplace.managerbyemployee.ManagePanel',

    getWorkplaceGrid: function(cfg_window, cfg) {
        if(!this._workplaceGrid){
            cfg = core.nullValue(cfg, {});
            Ext.apply(
                cfg,
                {
                    title: 'Locais de Lotação',
                    region: 'north',
                    split: true,
                    minHeight: 250,
                    height: 300,
                    columnAction: false,
                    hideActions: ['edit', ],
                    hideItemsToolbar: ['add', 'remove'],
                }
            );
            this._workplaceGrid = Ext._create('rh.workplace.Grid', cfg);

            this._workplaceGrid.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, record) {
                    this.workplace(record.get('pk'));
                },
                rowdeselect: function(sm) {
                    this.workplace(null);
                }
            });

            this._workplaceGrid.getStore().on({
                scope: this,
                load: function() {
                    this.workplace(null);
                }
            });

            this._workplaceGrid.getStore().on({
                scope: this,
                load: function() {
                    var selected = (this._workplaceGrid.getSelectionModel().getSelected());

                    if(selected)
                        this.workplace(selected.get('pk'));
                    else
                        this.workplace(null);
                }
            });
        }

        return this._workplaceGrid;
    },

    workplace: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._workplace = value;

            !prevent && this.observeWorkplace();
        }

        return this._workplace;
    },

    observeWorkplace: function() {
        var value = this.workplace();
        var grid;

        if(value) {
            grid = this.getEmployeeWorkplaceGrid();
            grid.setParam('lotacao', value);
            grid.setFilterProperty('lotacao', value, 6)
            grid.enable();

            this.getWorkassignmentGrid().enable();
            this.getWorkassignmentGrid().setParam('lotacao', value);
            this.getWorkassignmentGrid().setFilterProperty('lotacao', value, 6);
        }
        else {
            grid = this.getEmployeeWorkplaceGrid();
            grid.disable();
            grid.setParam('lotacao', 0);
            grid.setFilterProperty('lotacao', 0, 6, false);
            grid.getStore().removeAll();

            this.getWorkassignmentGrid().disable();
            this.getWorkassignmentGrid().setParam('lotacao', 0);
            this.getWorkassignmentGrid().setParam('child_of', undefined);
            this.getWorkassignmentGrid().setParam('lotacao', undefined);
            this.getWorkassignmentGrid().setParam('movimentacao_posse', undefined);
            this.getWorkassignmentGrid().setParam('servidor', undefined);

            this.getWorkassignmentGrid().setFilterProperty('lotacao', 0, 6, false);
            this.getWorkassignmentGrid().removeFilterProperty('child_of', 300, false);
        }
    },

    employeeWorkplace: function(record, prevent) {
        prevent = core.nullValue(prevent, false);
        if(record != undefined && record.get('pk') !== undefined) {
            this._employeeWorkplace = record.get('pk');
            this._workplace = record.get('lotacao');
            this._possession = record.get('movimentacao_posse');
            this._employee = record.get('servidor');
            this._type_by_possession = record.get('type_by_possession');

            !prevent && this.observeEmployeeWorkplace();
        }
        return this._employeeWorkplace;
    },

    observeEmployeeWorkplace: function() {
        if(this._employeeWorkplace != undefined) {
            this.getWorkassignmentGrid().setParam('child_of', this._employeeWorkplace);
            this.getWorkassignmentGrid().setParam('lotacao', this._workplace);
            this.getWorkassignmentGrid().setParam('movimentacao_posse', this._possession);
            this.getWorkassignmentGrid().setParam('servidor', this._employee);
            this.getWorkassignmentGrid().setParam('type_by_possession', this._type_by_possession);
            this.getWorkassignmentGrid().setFilterProperty('child_of', this._employeeWorkplace, 300);
        }
        else {
            this.getWorkassignmentGrid().setParam('child_of', undefined);
            this.getWorkassignmentGrid().setParam('lotacao', undefined);
            this.getWorkassignmentGrid().setParam('movimentacao_posse', undefined);
            this.getWorkassignmentGrid().setParam('servidor', undefined);
            this.getWorkassignmentGrid().setParam('type_by_possession',undefined);
            if(this.getWorkassignmentGrid().getParams().child_of != undefined){
                this.getWorkassignmentGrid().removeFilterProperty('child_of');
                this.getWorkassignmentGrid().getStore().reload();
            }
        }
    },

    getEmployeeWorkplaceGrid: function(cfg_window, cfg, gridClass) {
        if(!this._employeeWorkplaceGrid) {
            cfg = core.nullValue(cfg, {});
            this._employeeWorkplaceGrid = rh.employee.workplace.managerbyworkplace.ManagePanel.superclass.getEmployeeWorkplaceGrid.call(
                this,
                cfg_window,
                cfg,
                'rh.employee.workplace.managerbyworkplace.WorkplaceGrid'
            );
        }

        return this._employeeWorkplaceGrid;
    },

    getWorkassignmentGrid: function(cfg_window, cfg, gridClass) {
        if(!this._workassignmentGrid) {
            cfg = core.nullValue(cfg, {});
            this._workassignmentGrid = rh.employee.workplace.managerbyworkplace.ManagePanel.superclass.getWorkassignmentGrid.call(
                this,
                cfg_window,
                cfg,
                'rh.employee.workplace.managerbyworkplace.WorkassignmentGrid'
            );
        }
        return this._workassignmentGrid;
    },

    firstCall: function(){
        this.workplace(null);
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {});
        Ext.apply(
            cfg,
            {
                layout: 'border',
                border: false,
                items: [
                    this.getWorkplaceGrid(),
                    {
                        region: 'center',
                        layout: 'border',
                        border: false,
                        minHeight: 150,
                        bodyStyle: {
                            'border-left': 0,
                            'border-right': 0
                        },
                        layoutConfig: {
                            align: 'stretch'
                        },
                        items: [
                            this.getEmployeeWorkplaceGrid(cfg, {departament: cfg.departament}),
                            this.getControlPanel(),
                            this.getWorkassignmentGrid(cfg, {departament: cfg.departament})
                        ]
                    }
                ]
            }
        );
        rh.employee.workplace.managerbyworkplace.ManagePanel.superclass.constructor.call(this, cfg);
    }
});

