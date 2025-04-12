/**
 *
 **/
Ext._define('rh.hoursworkcontract.manager.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getHoursWorkContract: function() {
        if(!this._hoursWorkContract){
            this._hoursWorkContract = Ext._create('rh.hoursworkcontract.Grid', {
                region: 'center',
                border: false,
                split: true,
                minHeight: 250,
            });

            this._hoursWorkContract.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, record) {
                    this.hourContract(record.get('pk'));
                },
                rowdeselect: function(sm) {
                    this.hourContract(null);
                }
            });

            this._hoursWorkContract.getStore().on({
                scope: this,
                load: function() {
                    this.hourContract(null);
                }
            });

            this._hoursWorkContract.getStore().on({
                scope: this,
                load: function() {
                    var selected = (this._hoursWorkContract.getSelectionModel().getSelected());

                    if(selected)
                        this.hourContract(selected.get('pk'));
                    else
                        this.hourContract(null);
                }
            });
        }

        return this._hoursWorkContract;
    },

    hourContract: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._hourCountract = value;

            !prevent && this.observeHourContract();
        }

        return this._hourCountract;
    },

    observeHourContract: function() {
        var value = this.hourContract();
        var grid;

        if(value) {
            grid = this.getWorkHourIntervalGrid();
            grid.setParam('hours_work_contract', value);
            grid.setFilterProperty('hours_work_contract', value, 1001);
            grid.enable();
        }
        else {
            grid = this.getWorkHourIntervalGrid();
            grid.setParam('hours_work_contract', 0);
            grid.setFilterProperty('hours_work_contract', 0, 1001, false);
            grid.getStore().removeAll();
            grid.disable();
        }
    },

    getWorkHourIntervalGrid: function(args) {
        if(!this._workHourInterval)
            this._workHourInterval = Ext._create('rh.workhourinterval.Grid', {
                title: 'Intervalos de Horário de Trabalho',
                hours_work_contract: args.hours_work_contract,
                region: 'south',
                border: false,
                gridAutoLoad: false,
                minHeight: 300,
                height: 350,
            });
        return this._workHourInterval;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.apply(
            cfg,
            {
                title: 'Contratos Horário de Trabalho',
                layout: 'border',
                items: [
                    this.getHoursWorkContract(),
                    this.getWorkHourIntervalGrid({hours_work_contract: cfg.hours_work_contract}),
                ]
            }
        );

        rh.hoursworkcontract.manager.Manage.superclass.constructor.call(this, cfg);
    }
});

