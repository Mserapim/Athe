/**
 *
 **/

Ext._define('rh.registration.forminformation.dependente.DependenteManage', {
	extend: 'toolkit.widget.TabPanel',

	dependente: function(value, dispatch){
		dispatch = core.nullValue(dispatch, true);

		if(value !== undefined){
			this._dependente = value;

			if(dispatch) this.observeDependente();
		}
		else
			return this._dependente;
	},

	getGridDependente: function() {
		if(!this._gridDependente)
			this._gridDependente = Ext._create('rh.registration.forminformation.dependente.DependenteGrid', {
				region: 'center',
			});
			this._gridDependente.getSelectionModel().on({
				scope: this,
				rowselect: function(sm, index, data){
					this.dependente(data.get('pk'));
				},
				rowdeselect: function(){ 
					this.dependente(null);
				},
			});
			this._gridDependente.getStore().on({
				scope: this,
				load: function(gd, opts){
					var rec = this._gridDependente.getSelectionModel().getSelected();
					this._gridDependente.getSelectionModel().clearSelections();
					this.dependente(null);
					if(rec){
						this._gridDependente.getSelectionModel().selectRecords([rec]);
					}

				}
			})			

		return this._gridDependente;
	},

	getGridDependencia: function() {
		if(!this._gridDependencia)
			this._gridDependencia = Ext._create('rh.dependente.DependenciaGrid', {
				region: 'south',
				height: 300,
				gridAutoLoad: false,				
				// values: {servidor: this.dependente(),},
				// params: {end_validity: null},				
				hideColumns: [
					'unicode',
				]
			});

		return this._gridDependencia;
	},

	observeDependente: function() {
		if(this.dependente()){
			this.getGridDependencia().enable();
			this.getGridDependencia().setParam('dependente', this.dependente());
			this.getGridDependencia().setFilterProperty('dependente_id', this.dependente(), 100);
		}
		else{
			this.getGridDependencia().disable();
			this.getGridDependencia().getStore().removeAll();
			this.getGridDependencia().setFilterProperty('dependente_id', 0, 100, false);
		}
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Dependentes'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: [
					this.getGridDependente(),
					this.getGridDependencia()
				]
			}
		);

		rh.dependente.DependenteManage.superclass.constructor.call(this, cfg);
	}
});


Ext._define('rh.registration.forminformation.dependente.DependenteManageWindow', {
	extend: 'Ext.Window',

	dependente: function(value, dispatch){
		dispatch = core.nullValue(dispatch, true);

		if(value !== undefined){
			this._dependente = value;

			if(dispatch) this.observeDependente();
		}
		else
			return this._dependente;
	},

	getGridDependente: function(cfg) {
		if(!this._gridDependente){
			this._gridDependente = Ext._create('rh.registration.forminformation.dependente.DependenteGrid', {
				region: 'center',
				gridAutoLoad: true,
				height: 350,
			});

			this._gridDependente.getSelectionModel().on({
				scope: this,
				rowselect: function(sm, index, data){
					this.dependente(data.get('pk'));
				},
				rowdeselect: function(){ 
					this.dependente(null);
				},
			});
			this._gridDependente.getStore().on({
				scope: this,
				load: function(gd, opts){
					var rec = this._gridDependente.getSelectionModel().getSelected();
					this._gridDependente.getSelectionModel().clearSelections();
					this.dependente(null);
					if(rec){
						this._gridDependente.getSelectionModel().selectRecords([rec]);
					}
				}
			});
            this._gridDependente.setFilterProperty('servidor', cfg['servidor']);
            this._gridDependente.setParam('servidor', cfg['servidor']);
		}
		return this._gridDependente;
	},

	getGridDependencia: function() {
		if(!this._gridDependencia)
			this._gridDependencia = Ext._create('rh.registration.forminformation.dependente.DependenciaGrid', {
				region: 'south',
				height: 250,
				// values: {servidor: this.dependente(),},
				// params: {end_validity: null},
				gridAutoLoad: false,
				hideColumns: [
					'unicode',
				]
			});

		return this._gridDependencia;
	},

	observeDependente: function() {
		if(this.dependente()){
			this.getGridDependencia().enable();
			this.getGridDependencia().setParam('dependente', this.dependente());
			this.getGridDependencia().setFilterProperty('dependente_id', this.dependente(), 100);
		}
		else{
			this.getGridDependencia().disable();
			this.getGridDependencia().getStore().removeAll();
			this.getGridDependencia().setFilterProperty('dependente_id', 0, 100, false);
		}
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};
		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Dependentes'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				height: 600,
				width: 800,
				items: [
					this.getGridDependente(cfg),
				]
			}
		);
		rh.registration.forminformation.dependente.DependenteManage.superclass.constructor.call(this, cfg);
	}
});