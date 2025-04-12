/**
 *
 **/

Ext._define('rh.gfp.transparencychoice.genreevent.TransparencyManage', {
	extend: 'toolkit.widget.TabPanel',

	getTransparencyChoiceGrid: function() {
		if(!this._transparencyChoiceGrid) {
			this._transparencyChoiceGrid = Ext._create('rh.gfp.transparencychoice.Grid', {
				region: 'north',
				split: true,
				minHeight: 200,
				height: 200,
				hideActions: ['remove']
			});

			this._transparencyChoiceGrid.setFilterProperty('active__in', [true, ], 1);

			this._transparencyChoiceGrid.getSelectionModel().on({
				scope: this,
				selectionchange: function(selm) {
					if(selm.getSelections().length > 0)
						this.transparencyChoice(selm.getSelections()[0].get('value'));
					else
						this.transparencyChoice(null);
				}
			});
		}

		return this._transparencyChoiceGrid;
	},

	transparencyChoice: function(value, dispatch) {
	    dispatch = (dispatch === undefined ? true : dispatch);

	    if(value !== undefined) {
	        this._transparencyChoice = value;

	        if(dispatch)
	            this.observeTransparencyChoice();
	    }

	    return this._transparencyChoice;
	},

	observeTransparencyChoice: function() {
	    var value = this.transparencyChoice();

	    if(value) {
			this.getControlPanel().enable();
			this.getGenreEventSelectedGrid().enable();
			this.getGenreEventSelectedGrid().setParam('config_transparency', value);
			this.getGenreEventSelectedGrid().setFilterProperty('config_transparency', value, 100);
	    }
	    else {
			this.getControlPanel().disable();
			this.getGenreEventSelectedGrid().disable();
			this.getGenreEventSelectedGrid().setParam('config_transparency', 0);
			this.getGenreEventSelectedGrid().setFilterProperty('config_transparency', 0, 100, false);
			this.getGenreEventSelectedGrid().getStore().removeAll();
	    }
	},

	_addConfigTransparency: function(pkset) {
		var rest = this.getGenreEventGrid().factoryRestful();
		var mask = new Ext.LoadMask(this.getEl(), {msg: 'adicionando itens...'});

		mask.show();
		rest.manageConfigTransparency(
			pkset,
			this.transparencyChoice(),
			'add_config_transparency',
			{
				scope: this,
				fn: function() {
					this.getGenreEventGrid().getStore().reload();
					this.getGenreEventSelectedGrid().getStore().reload();
					this.getTransparencyChoiceGrid().getStore().reload();
				}
			},
			{
				fn: function(message) {
					Ext.Msg.show({
					    title: 'Adicionando',
					    msg: message,
					    icon: Ext.Msg.ERROR,
					    buttons: Ext.Msg.OK
					});
				}
			},
			{
				fn: function() {
					mask.hide();
				}
			}
		);
	},

	addConfigTransparency: function(selected) {
		selected = (selected || this.getGenreEventGrid().getSelectionModel().getSelections());

		if(selected.length > 0)
			this._addConfigTransparency(selected.map(function(data) { return data.get('pk'); }));
		else
			Ext.Msg.show({
			    title: 'Adicionando itens',
			    msg: 'Primeiro selecione os itens que deseja adicionar.',
			    icon: Ext.Msg.ERROR,
			    buttons: Ext.Msg.OK
			});
	},

	_removeConfigTransparency: function(pkset) {
		var rest = this.getGenreEventGrid().factoryRestful();
		var mask = new Ext.LoadMask(this.getEl(), {msg: 'removendo itens...'});

		mask.show();
		rest.manageConfigTransparency(
			pkset,
			this.transparencyChoice(),
			'remove_config_transparency',
			{
				scope: this,
				fn: function() {
					this.getGenreEventGrid().getStore().reload();
					this.getGenreEventSelectedGrid().getStore().reload();
					this.getTransparencyChoiceGrid().getStore().reload();
				}
			},
			{
				fn: function(message) {
					Ext.Msg.show({
					    title: 'Removendo',
					    msg: message,
					    icon: Ext.Msg.ERROR,
					    buttons: Ext.Msg.OK
					});
				}
			},
			{
				fn: function() {
					mask.hide();
				}
			}
		);
	},

	removeConfigTransparency: function(selected) {
		selected = (selected || this.getGenreEventSelectedGrid().getSelectionModel().getSelections());

		if(selected.length > 0)
			this._removeConfigTransparency(selected.map(function(data) { return data.get('pk'); }));
		else
			Ext.Msg.show({
			    title: 'Removendo itens',
			    msg: 'Primeiro selecione os itens que deseja remover.',
			    icon: Ext.Msg.ERROR,
			    buttons: Ext.Msg.OK
			});
	},

	getControlPanel: function() {
	    if(!this._controlPanel)
	        this._controlPanel = Ext._create('Ext.Panel', {
	            width: 40,
	            frame: true,
	            layout: 'vbox',
	            bodyStyle: {
	                'border-top': 0,
	                'border-bottom': 0
	            },
	            items: [
	                {
	                    xtype: 'panel',
	                    flex: 1.0
	                },

   					{
	                    xtype: 'button',
						iconCls: 'icon-core icon-core-add-selected',
	                    width: 28,
	                    height: 30,
	                    style: {
	                        padding: '2px 0 0 0'
	                    },
	                    scope: this,
	                    handler: function() { this.addConfigTransparency(); }
	                },

	                {
	                    xtype: 'button',
						iconCls: 'icon-core icon-core-remove-selected',
	                    width: 28,
	                    height: 30,
	                    style: {
	                        padding: '2px 0 0 0'
	                    },
	                    scope: this,
	                    handler: function() { this.removeConfigTransparency(); }
	                },

	                {
	                    xtype: 'button',
						iconCls: 'icon-core icon-core-add-all',
	                    width: 28,
	                    height: 30,
	                    style: {
	                        padding: '2px 0 0 0'
	                    },
	                    scope: this,
	                    handler: function() {
							var collection = [];

							this.getGenreEventGrid().getStore().each(
								function(data) {
									collection.push(data);
								}
							);

							this.addConfigTransparency(collection);
						}
	                },

	                {
	                    xtype: 'button',
						iconCls: 'icon-core icon-core-remove-all',
	                    width: 28,
	                    height: 30,
	                    style: {
	                        padding: '2px 0 0 0'
	                    },
	                    scope: this,
	                    handler: function() {
							var collection = [];

							this.getGenreEventSelectedGrid().getStore().each(
								function(data) {
									collection.push(data);
								}
							);

							this.removeConfigTransparency(collection);
						}
	                },

	                {
	                    xtype: 'panel',
	                    flex: 1.0
	                }
	            ]
	        });

	    return this._controlPanel;
	},

	getGenreEventSelectedGrid: function() {
	    if(!this.__genreEventSelectedGrid) {
			var self = this;

	        this.__genreEventSelectedGrid = Ext._create('rh.gfp.payroll.GenreEventGrid', {
	            title: 'Gêneros Selecionados',
	            flex: 1.0,
				doubleClickHandler: function() {
					self.removeConfigTransparency();
				},
	            border: false,
	            gridAutoLoad: false,
	            configOrderToolBar: ['search',],
	            columnAction: false,
	        });

	    }
	    return this.__genreEventSelectedGrid;
	},

	getGenreEventGrid: function() {
	    if(!this._genreEventGrid) {
			var self = this;

	        this._genreEventGrid = Ext._create('rh.gfp.payroll.GenreEventGrid', {
	            title: 'Gêneros',
	            flex: 1.0,
				doubleClickHandler: function() {
					self.addConfigTransparency();
				},
	            border: false,
	            configOrderToolBar: ['search',],
				columnAction: false
	        });
	    }
	    return this._genreEventGrid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Eventos Portal da Transparência'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				border: false,
				items: [
					this.getTransparencyChoiceGrid(),
					{
                	    region: 'center',
                        layout: 'hbox',
                        minHeight: 150,
                        bodyStyle: {
                            'border-left': 0,
                            'border-right': 0
                        },
                        layoutConfig: {
                            align: 'stretch'
                        },
                        items: [
                            this.getGenreEventGrid(),
                            this.getControlPanel(),
                            this.getGenreEventSelectedGrid()
                        ]
                    }
				]
			}
		);

		rh.gfp.transparencychoice.genreevent.TransparencyManage.superclass.constructor.call(this, cfg);
		this.observeTransparencyChoice();
	}
});
