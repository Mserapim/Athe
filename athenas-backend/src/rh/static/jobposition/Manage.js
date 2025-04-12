/**
 *
 **/

Ext._define('rh.jobposition.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.jobposition.Grid', {
				region: 'center',
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
            this._configGrid = Ext._create('rh.jobposition.config.Grid', {
                title: 'Configuração do Cargo',
                region: 'south',
                split: true,
                flex: 0.5,
                height: 400,
                split: true,
                gridAutoLoad: false
            });
            var owner = this;
            this._configGrid.on({
                scope: this,
                createdItemGrid: function(instance) {
                    owner.getGrid().getStore().load();
                },
                updatedItemGrid: function(instance) {
                    owner.getGrid().getStore().load();
                },
                removedItemGrid: function(instance) {
                    owner.getGrid().getStore().load();
                }
            });
        }
        return this._configGrid;
    },

    config: function(value, dispatch){
        dispatch = core.nullValue(dispatch, true)

        if(value !== undefined){
            this._config = value;

            if(dispatch) this.observeJobPosition();
        }
        else
            return this._config;
    },

    observeJobPosition: function(){
        if(this.config()){
            this.configGrid().enable();
            this.configGrid().setParam('job_position', this.config());
            this.configGrid().setFilterProperty('job_position_id', this.config(), 100);
        }
        else{
            this.configGrid().disable();
            this.configGrid().getStore().removeAll();
            this.configGrid().setFilterProperty('job_position_id', 0, 100, false);
        }
    },

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Cargos'
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

		rh.jobposition.Manage.superclass.constructor.call(this, cfg);
	}
});
