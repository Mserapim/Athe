/**
 *
 **/

Ext._define('rh.gfp.payroll.GenreEventManage', {
	extend: 'toolkit.widget.TabPanel',

	getGenreGrid: function() {
		if(!this._grid){
			this._grid = Ext._create('rh.gfp.payroll.GenreEventGrid', {
				// specieGrid: null,
				eventGrid: null,
				region: 'center',
				width: '50%',
				height: '50%',
				minHeight: 300,
				split: true
			});

			this._grid.eventGrid = this.getEventGrid();
		}

		this._grid.getSelectionModel().on({
				scope: this,
				rowselect: function(sm, index, data){
					this.genre(data.get('pk'));
				},
				rowdeselect: function(){ 
					this.genre(null);
				},
		});

		return this._grid;
	},

	getEventGrid: function() {
		if(!this._eventGrid){
	        this._eventGrid = Ext._create('rh.gfp.payroll.EventGrid', {
	        	region: 'south',
				minHeight: 400,
				height: 400,
				split: true,
	        });
		}
	
	    return this._eventGrid;
	},

	genre: function(value, dispatch){
		dispatch = core.nullValue(dispatch, true);
		if(value !== undefined){
			this._genre = value;

			if(dispatch) this.observeGenre();
		}
		else
			return this._genre;
	},

	observeGenre: function(){
		if(this.genre()){
			this.getEventGrid().setParam('genre_event', this.genre());
			this.getEventGrid().setFilterProperty('genre_event_id', this.genre(), 100);
		}
		else{
			this.getEventGrid().getStore().removeAll();
			this.getEventGrid().setFilterProperty('genre_event_id', null, 100, false);
			this.getEventGrid().getStore().reload();
		}
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Eventos'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items:[
					this.getGenreGrid(),
					this.getEventGrid(),
				]
			}
		);

		rh.gfp.payroll.GenreEventManage.superclass.constructor.call(this, cfg);
	}

	
});
