/**
 *
 **/
 Ext._define('judicial.county.ExecutionOrganManage', {
    extend: 'toolkit.widget.TabPanel',

    getExecutionOrganGrid: function() {
        if(!this._executionOrgan){
            this._executionOrgan = Ext._create('judicial.county.ExecutionOrganGrid', {
                region: 'north',
                split: true,
                minHeight: 450,
                height: 450
            });

            this._executionOrgan.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, record) {
                    this.location(record.get('localidade'));
                    this.execution(record.get('pk'));
                },
                rowdeselect: function(sm) {
                    this.location(null);
                    this.execution(null);
                }
            });

            this._executionOrgan.getStore().on({
                scope: this,
                load: function() {
                    this.location(null);
                    this.execution(null);
                }
            });

            this._executionOrgan.getStore().on({
                scope: this,
                load: function() {
                    var selected = (this._executionOrgan.getSelectionModel().getSelected());

                    if(selected)
                        this.execution(selected.get('pk'));
                    else
                        this.execution(null);
                }
            });
        }

        return this._executionOrgan;
    },

    location: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._location = value;

            if(!prevent) this.observeLocation();
        }

        return this._location;
    },

    observeLocation: function() {
        var value = this.location();

        if(value) {
            this.getDistributionTableGrid().setParam('__location', value);
        }
        else {
            this.getDistributionTableGrid().setParam('__location', 0);
        }
    },

    execution: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._execution = value;

            !prevent && this.observeExecution();
        }

        return this._execution;
    },

    observeExecution: function() {
        var value = this.execution();
        var grid;

        if(value) {
            grid = this.getDistributionTableGrid();
            grid.setParam('execution_organ', value);
            grid.setFilterProperty('execution_organ', value, 1001)
            grid.enable();
        }
        else {
            grid = this.getDistributionTableGrid();
            grid.setParam('execution_organ', 0);
            grid.setFilterProperty('execution_organ', 0, 1001, false);
            grid.getStore().removeAll();
            grid.disable();
        }
    },

    getDistributionTableGrid: function() {
        if(!this._distributionTableGrid)
            this._distributionTableGrid = Ext._create('judicial.county.DistributionTableGrid', {
                region: 'center',
                gridAutoLoad: false,
                minHeight: 300
            });

        return this._distributionTableGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Orgãos de Execução',
            }
        );

        Ext.apply(
            cfg,
            {
                border: false,
                layout: 'border',
                items: [
                    this.getExecutionOrganGrid(),
                    this.getDistributionTableGrid()
                ]
            }
        );

        this.is_time = 0;

        judicial.county.ExecutionOrganManage.superclass.constructor.call(this, cfg);
        this.execution(null);
    }
});

