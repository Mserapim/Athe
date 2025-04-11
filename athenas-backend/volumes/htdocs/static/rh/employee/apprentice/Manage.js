 Ext._define('rh.employee.apprentice.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getEmployeeGrid: function(cfg) {
        if(!this._employeeGrid){
            this._employeeGrid = Ext._create('rh.employee.apprentice.Grid', {
                title: 'Jovem Cidadão - Aprendiz',
                region: 'north',
                border: false,
                split: true,
                minHeight: 450,
                height: 550,
                columnAction: false,
                matriculaFieldBlocked: cfg.matriculaFieldBlocked,
                restWindow: 'rh.employee.apprentice.Window',
            });

            this._employeeGrid.setFilterProperty('tipo__in', 'A', 1002, true);

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
            grid = this.getDeclarationActivityGrid();
            grid.setParam('servidor', value);
            grid.setFilterProperty('servidor', value, 1001)
            grid.enable();
        }
        else {
            grid = this.getDeclarationActivityGrid();
            grid.setParam('servidor', 0);
            grid.setFilterProperty('servidor', 0, 1001, false);
            grid.getStore().removeAll();
            grid.disable();
        }
    },

    getDeclarationActivityGrid: function() {
        if(!this._declarationActivityGrid){
            this._declarationActivityGrid = Ext._create('rh.declarationactivity.Grid', {
                title: 'Declaração de Atividade',
                region: 'center',
                gridAutoLoad: false,
                minHeight: 300
            });
            this._declarationActivityGrid.setFilterProperty('servidor__tipo', 'A', 1, false);
        }
        return this._declarationActivityGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Jovem Cidadão - Aprendiz',
            }
        );

        Ext.apply(
            cfg,
            {
                border: false,
                layout: 'border',
                items: [
                    this.getEmployeeGrid(cfg),
                    this.getDeclarationActivityGrid()
                ]
            }
        );

        rh.employee.apprentice.Manage.superclass.constructor.call(this, cfg);
        this.employee(null);
    }
});

