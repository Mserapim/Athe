/**
 *
 **/
Ext._define('rh.hoursworkcontract.workload.manager.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getWorkloadGrid: function() {
        if(!this._cworkloadGrid) {
            this._cworkloadGrid = Ext._create('rh.hoursworkcontract.workload.manager.Grid', {
                region: 'center',
                border: false,
                split: true,
                minHeight: 250,
            });
        }
        this._cworkloadGrid.getSelectionModel().on({
            scope: this,
            rowselect: function(sm, index, record) {
                this.hourContractWorkload(record.get('pk'));
            },
            rowdeselect: function(sm) {
                this.hourContractWorkload(null);
            }
        });

        this._cworkloadGrid.getStore().on({
            scope: this,
            load: function() {
                this.hourContractWorkload(null);
            }
        });

        this._cworkloadGrid.getStore().on({
            scope: this,
            load: function() {
                var selected = (this._cworkloadGrid.getSelectionModel().getSelected());

                if(selected)
                    this.hourContractWorkload(selected.get('pk'));
                else
                    this.hourContractWorkload(null);
            }
        });
        return this._cworkloadGrid;
    },

    hourContractWorkload: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._hourCountract = value;

            !prevent && this.observeHourContractWorkload();
        }

        return this._hourCountract;
    },

    observeHourContractWorkload: function() {
        var value = this.hourContractWorkload();
        var grid;

        if(value) {
            grid = this.getEmployeeWorkloadGrid();
            grid.setParam('hours_work_contract_workload', value);
            grid.addFilterProperty('hours_work_contract_workload', value, 1001, false);
            grid.clearAllFilter();
            grid.enable();
        }
        else {
            grid = this.getEmployeeWorkloadGrid();
            grid.setParam('hours_work_contract_workload', 0);
            grid.addFilterProperty('hours_work_contract_workload', 0, 1001, false);
            grid.disable();
        }
    },

    getEmployeeWorkloadGrid: function(args) {
        if(!this._employeeWorkloadGrid)
            this._employeeWorkloadGrid = Ext._create('rh.hoursworkcontract.employeeworkload.Grid', {
                title: 'Servidores da Escala',
                region: 'south',
                border: false,
                gridAutoLoad: false,
                minHeight: 300,
                height: 350,
            });
        return this._employeeWorkloadGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {title: 'Gestor de Escalas',});
        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getWorkloadGrid(),
                    this.getEmployeeWorkloadGrid({hours_work_contract_workload: cfg.hours_work_contract_workload}),
                ]
            }
        );

        rh.hoursworkcontract.workload.manager.Manage.superclass.constructor.call(this, cfg);
    }
});
