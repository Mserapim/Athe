Ext._define('rh.employee.retiree.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getEmployeeGrid: function() {
        if(!this._employeeGrid){
            this._employeeGrid = Ext._create('rh.employee.retiree.Grid', {
                title: 'Aposentado',
                region: 'north',
                border: false,
                split: true,
                minHeight: 350,
                height: 350,
                columnAction: false,
                restWindow: 'rh.employee.retiree.Window',
            });

            this._employeeGrid.setFilterProperty('tipo__in', 'O', 1002, true);

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
            grid = this.getDeclarationActivityRetireeGrid();
            grid.setParam('servidor', value);
            grid.setFilterProperty('servidor', value, 1001)
            grid.enable();
        }
        else {
            grid = this.getDeclarationActivityRetireeGrid();
            grid.setParam('servidor', 0);
            grid.setFilterProperty('servidor', 0, 1001, false);
            grid.getStore().removeAll();
            grid.disable();
        }
    },

    getDeclarationActivityRetireeGrid: function() {
        if(!this._declarationActivityRetireeGrid){
            this._declarationActivityRetireeGrid = Ext._create('rh.declarationactivityretiree.Grid', {
                title: 'Declaração de Atividade',
                region: 'center',
                gridAutoLoad: false,
                minHeight: 300
            });
            this._declarationActivityRetireeGrid.setFilterProperty('servidor__tipo', 'O', 1, false);
        }
        return this._declarationActivityRetireeGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Aposentados',
            }
        );

        Ext.apply(
            cfg,
            {
                border: false,
                layout: 'border',
                items: [
                    this.getEmployeeGrid(),
                    this.getDeclarationActivityRetireeGrid()
                ]
            }
        );

        rh.employee.retiree.Manage.superclass.constructor.call(this, cfg);
        this.employee(null);
    }
});

