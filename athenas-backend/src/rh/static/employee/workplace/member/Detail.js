/**
 *
 **/
 Ext._define('rh.employee.workplace.member.Detail', {
    extend: 'toolkit.widget.TabPanel',

    getEmployeeGrid: function() {
        if(!this._employeeGrid){
            this._employeeGrid = Ext._create('rh.employee.Grid', {
                region: 'north',
                split: true,
                minHeight: 450,
                height: 450,
                columnAction: false
            });

            this._employeeGrid.setFilterProperty('ativo__in', [true], 1001, false);
            this._employeeGrid.setFilterProperty('tipo', 'M', 1002, false);

            this._employeeGrid.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, record) {
                    this.employee(record.get('pk'));
                },
                rowdeselect: function(sm) {
                    this.employee(null);
                }
            });

            this._employeeGrid.getStore().on({
                scope: this,
                load: function() {
                    this.employee(null);
                }
            });

            this._employeeGrid.getStore().on({
                scope: this,
                load: function() {
                    var selected = (this._employeeGrid.getSelectionModel().getSelected());

                    if(selected)
                        this.employee(selected.get('pk'));
                    else
                        this.employee(null);
                }
            });
        }

        return this._employeeGrid;
    },

    employee: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._employee = value;

            !prevent && this.observeEmployee();
        }

        return this._employee;
    },

    observeEmployee: function() {
        var value = this.employee();
        var grid;

        if(value) {
            grid = this.getEmployeeWorkplaceMemberGrid();
            grid.setParam('servidor', value);
            grid.setFilterProperty('servidor', value, 1001);
            grid.enable();
        }
        else {
            grid = this.getEmployeeWorkplaceMemberGrid();
            grid.setParam('servidor', 0);
            grid.setFilterProperty('servidor', 0, 1001, false);
            grid.getStore().removeAll();
            grid.disable();
        }
    },

    getEmployeeWorkplaceMemberGrid: function() {
        if(!this._EmployeeWorkplaceMemberGrid)
            this._EmployeeWorkplaceMemberGrid = Ext._create('rh.employee.workplace.member.Grid', {
                region: 'center',
                gridAutoLoad: false,
                minHeight: 300
            });
        return this._EmployeeWorkplaceMemberGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Membros e Designações',
            }
        );

        Ext.apply(
            cfg,
            {
                border: false,
                layout: 'border',
                items: [
                    this.getEmployeeGrid(),
                    this.getEmployeeWorkplaceMemberGrid()
                ]
            }
        );

        rh.employee.workplace.member.Detail.superclass.constructor.call(this, cfg);
        this.employee(null);
    }
});

