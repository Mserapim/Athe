/**
 *
 **/
Ext._define('rh.hoursworkcontract.workload.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getWorkloadGrid: function() {
        if(!this._cworkloadGrid) {
            this._cworkloadGrid = Ext._create('rh.hoursworkcontract.workload.Grid', {
                region: 'center',
            });
        }
        return this._cworkloadGrid;
    },

    getWorkHourGrid: function() {
        if(!this._configuracaogrid) {
            this._configuracaogrid = Ext._create('rh.hoursworkcontract.workload.Grid', {
                region: 'south',
                height: 400,
                title: 'Horários e dias',
                disabled: true,
                gridAutoLoad: false,
            });
        }
        return this._configuracaogrid;
    },

    observe: function(value, prevent) {
        prevent = core.nullValue(prevent, false);
        if(value !== undefined) {
            this._param = value;
            if(!prevent)
                this.observeHour();
        }
        return this._param;
    },

     observeHour: function(){
        var value = this.observe();
        if(value) {
            this.getWorkHourGrid().enable();
            this.getWorkHourGrid().setFilterProperty('workload', value);
            this.getWorkHourGrid().setParam('workload', value);
        }
        else {
            this.getWorkHourGrid().getStore().removeAll();
            this.getWorkHourGrid().disable();
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {title: 'Gestor de Horários Diários'});

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getWorkloadGrid(),
                ]
            }
        );

        rh.hoursworkcontract.workload.Manage.superclass.constructor.call(this, cfg);
    }
});
