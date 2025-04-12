/**
 *
 **/

Ext._define('rh.carreira.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.carreira.Grid', {
				region: 'center'
			});

        this._grid.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, data){
                    this.config(data.get('pk'));
                },
                rowdeselect: function(){
                    this.config(null);
                },
        });

        return this._grid;
    },

    configGrid: function(){
        if(!this._configGrid){
            this._configGrid = Ext._create('rh.carreira.config.Grid', {
                region: 'south',
                // heigth: "50%",
                split: true,
                // allEvent: this,
                flex: 0.5,
                height: 400,
                split: true,
                gridAutoLoad: false
            });
        }
        return this._configGrid;
    },

    config: function(value, dispatch){
        dispatch = core.nullValue(dispatch, true)

        if(value !== undefined){
            this._config = value;

            if(dispatch) this.observeCareer();
        }
        else
            return this._config;
    },

    observeCareer: function(){
        if(this.config()){
            this.configGrid().enable();
            this.configGrid().setParam('career', this.config());
            this.configGrid().setFilterProperty('career_id', this.config(), 100);
        }
        else{
            this.configGrid().disable();
            this.configGrid().getStore().removeAll();
            this.configGrid().setFilterProperty('career_id', 0, 100, false);
        }
    },

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Carreiras'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items:[
					this.getGrid(),
					this.configGrid(),
				]
			}
		);

		rh.carreira.Manage.superclass.constructor.call(this, cfg);
	}
});
