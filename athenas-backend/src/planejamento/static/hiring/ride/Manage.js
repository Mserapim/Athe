Ext._define('planning.hiring.ride.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getRideGrid: function() {
        if(!this._rideGrid) {
            this._rideGrid = Ext._create('planning.hiring.ride.Grid', {
                region: 'center'
            });

            this._rideGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function (selm) {
                    var selection = selm.getSelections();
                    if (selection.length > 0) {
                        this.ride(selection[0].id);
                    } else {
                        this.ride(null);
                    }
                }
            });

            this._rideGrid.getStore().on({
                scope: this,
                load: function () {
                    this.observeRide();
                }
            });
        }

        return this._rideGrid;
    },

    ride: function (value, observe) {
        observe = (observe === undefined ? true : observe);

        if (value !== undefined) {
            this._ride = value;

            if (observe)
                this.observeRide();
        }

        return this._ride;
    },

    observeRide: function() {
        var value = this.ride();
        var selected = this.getRideGrid().getSelectionModel().getSelected();
        minute = 0
        if(selected != null)
            minute = selected.data.minute;
        var rideItemGrid = this.getRideItemGrid();

        if(value) {
            rideItemGrid.enable();
            rideItemGrid.setParam('ride', value);
            rideItemGrid.setParam('minute', minute);
            rideItemGrid.setFilterProperty('ride', value, 10);
        } else {
            rideItemGrid.disable();
            rideItemGrid.setParam('ride', 0);
            rideItemGrid.setParam('minute', 0);
            rideItemGrid.getStore().removeAll();
            rideItemGrid.setFilterProperty('ride', value, 10, false);
        }
    },

    getRideItemGrid: function() {
        if(!this._rideItemGrid) {
            this._rideItemGrid = Ext._create('planning.hiring.rideitem.GridBottom', {
                title: 'Itens Adquiridos',
                region: 'south',
                height: 300,
                gridAutoLoad: false
            });
        }

        return this._rideItemGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});[]

        Ext.applyIf(
            cfg,
            {
                title: 'Gerência de Caronas',
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getRideGrid(),
                    this.getRideItemGrid()
                ]
            }
        );

        planning.hiring.ride.Manage.superclass.constructor.call(this, cfg);
        this.observeRide();
    }
});
