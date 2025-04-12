/**
 *
 **/

 Ext._define('rh.defin.eventual_provider.pf.Manage', {
    extend: 'toolkit.widget.TabPanel',

    eventualProvider: function(value, dispatch){
		dispatch = core.nullValue(dispatch, true);
		if(value !== undefined){
			this._eventualProvider = value;

			if(dispatch) this.observeEventualProvider();
		}
		return this._eventualProvider;
	},

    observeEventualProvider: function() {
		if(this.eventualProvider()){
			this.getEventGrid().enable();
			this.getEventGrid().setParam('natural_person', this.eventualProvider().pk);
			this.getEventGrid().setFilterProperty('natural_person', this.eventualProvider().pk, 1000);
		}
		else{
			this.getEventGrid().disable();
			this.getEventGrid().getStore().removeAll();
			this.getEventGrid().setFilterProperty('natural_person', 0, 1000, false);
		}
	},

    getEventualProviderGrid: function(cfg) {
        if(!this._eventualProviderGrid){
            this._eventualProviderGrid = Ext._create('rh.defin.eventual_provider.pf.Grid', {
                region: 'center',
            });

            this._eventualProviderGrid.getSelectionModel().on({
				scope: this,
				rowselect: function(grid, index, record) {
					this.eventualProvider(record.data);
				},
				rowdeselect: function(grid, index, record){
					this.eventualProvider(null);
				}
			});

			this._eventualProviderGrid.getStore().on({
                scope: this,
                load: function () {
                    this.observeEventualProvider();
                }
            });
        }
        return this._eventualProviderGrid;
    },

    getEventGrid: function(cfg) {
		if(!this._events)
			this._events = Ext._create('rh.defin.entry.pf_provider.Grid', {
				region: 'south',
				gridAutoLoad: false,
				disabled: true,
				split: true,
				flex: 0.5,
				height: 400,
			});

		return this._events;
	},

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Lançador - Prestadores PF'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                defaults: {
					split: true,
				},
                items: [
                    this.getEventualProviderGrid(cfg),
                    this.getEventGrid(cfg)
                ]
            }
        );

        rh.defin.eventual_provider.pf.Manage.superclass.constructor.call(this, cfg);
        this.observeEventualProvider();
    }
});
