/**
 *
 **/

Ext._define('edocs.protocolo.GroupPersonManage', {
	extend: 'toolkit.widget.TabPanel',

	getGroupPersonGrid: function() {
		if(!this._groupPersonGrid) {
			this._groupPersonGrid = Ext._create('edocs.protocolo.GroupPersonGrid', {
				region: 'north',
				split: true,
				minHeight: 180,
				height: 180,
				hideActions: ['remove']
			});

			this._groupPersonGrid.getSelectionModel().on({
				scope: this,
				selectionchange: function(selm) {
					if(selm.getSelections().length > 0)
						this.groupPerson(selm.getSelections()[0].get('pk'));
					else
						this.groupPerson(null);
				}
			});
		}

		return this._groupPersonGrid;
	},

	groupPerson: function(value, dispatch) {
	    dispatch = (dispatch === undefined ? true : dispatch);

	    if(value !== undefined) {
	        this._groupPerson = value;

	        if(dispatch)
	            this.observeGroupPerson();
	    }

	    return this._groupPerson;
	},

	observeGroupPerson: function() {
	    var value = this.groupPerson();

	    if(value) {
			this.getControlPanel().enable();

			this.getPersonGrid().enable();
			this.getPersonGrid().setParam('in_group_person', value);
			this.getPersonGrid().setFilterProperty('in_group_person', value, -100);

			this.getPersonSelectedGrid().enable();
			this.getPersonSelectedGrid().setParam('in_group_person', value);
			this.getPersonSelectedGrid().setFilterProperty('in_group_person', value, 100);
	    }
	    else {
			this.getControlPanel().disable();

			this.getPersonGrid().disable();
			this.getPersonGrid().setParam('in_group_person', 0);
			this.getPersonGrid().setFilterProperty('in_group_person', 0, -100, false);
			this.getPersonGrid().getStore().removeAll();

			this.getPersonSelectedGrid().disable();
			this.getPersonSelectedGrid().setParam('in_group_person', 0);
			this.getPersonSelectedGrid().setFilterProperty('in_group_person', 0, 100, false);
			this.getPersonSelectedGrid().getStore().removeAll();
	    }
	},

	_addPersons: function(pkset) {
		var rest = this.getGroupPersonGrid().factoryRestful();
		var mask = new Ext.LoadMask(this.getEl(), {msg: 'adicionando itens...'});

		mask.show();
		rest.addPersons(
			this.groupPerson(),
			pkset,
			{
				scope: this,
				fn: function() {
					this.getPersonGrid().getStore().reload();
					this.getPersonSelectedGrid().getStore().reload();
					this.getGroupPersonGrid().getStore().reload();
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

	addPersons: function(selected) {
		selected = (selected || this.getPersonGrid().getSelectionModel().getSelections());

		if(selected.length > 0)
			this._addPersons(selected.map(function(data) { return data.get('pk'); }));
		else
			Ext.Msg.show({
			    title: 'Adicionando itens',
			    msg: 'Primeiro selecione os itens que deseja adicionar.',
			    icon: Ext.Msg.ERROR,
			    buttons: Ext.Msg.OK
			});
	},

	_removePersons: function(pkset) {
		var rest = this.getGroupPersonGrid().factoryRestful();
		var mask = new Ext.LoadMask(this.getEl(), {msg: 'removendo itens...'});

		mask.show();
		rest.removePersons(
			this.groupPerson(),
			pkset,
			{
				scope: this,
				fn: function() {
					this.getPersonGrid().getStore().reload();
					this.getPersonSelectedGrid().getStore().reload();
					this.getGroupPersonGrid().getStore().reload();
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

	removePersons: function(selected) {
		selected = (selected || this.getPersonSelectedGrid().getSelectionModel().getSelections());

		if(selected.length > 0)
			this._removePersons(selected.map(function(data) { return data.get('pk'); }));
		else
			Ext.Msg.show({
			    title: 'Adicionando itens',
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
	                    handler: function() { this.addPersons(); }
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
	                    handler: function() { this.removePersons(); }
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

							this.getPersonGrid().getStore().each(
								function(data) {
									collection.push(data);
								}
							);

							this.addPersons(collection);
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

							this.getPersonSelectedGrid().getStore().each(
								function(data) {
									collection.push(data);
								}
							);

							this.removePersons(collection);
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

	getPersonSelectedGrid: function() {
	    if(!this._personSelectedGrid) {
			var self = this;

	        this._personSelectedGrid = Ext._create('rh.person.Grid', {
	            title: 'Pessoas Selecionadas',
	            flex: 1.0,
				doubleClickHandler: function() {
					self.removePersons();
				},
	            border: false,
	            gridAutoLoad: false,
	            configOrderToolBar: ['search',],
	            columnAction: false,
	        });

	    }
	    return this._personSelectedGrid;
	},

	getPersonGrid: function() {
	    if(!this._personGrid) {
			var self = this;

	        this._personGrid = Ext._create('rh.person.Grid', {
	            title: 'Pessoas Disponíveis',
	            flex: 1.0,
				doubleClickHandler: function() {
					self.addPersons();
				},
	            border: false,
	            gridAutoLoad: false,
	            configOrderToolBar: ['search',],
				columnAction: false
	        });


			this._personGrid.setFilterProperty('enable_protocol', true, 1, false);

	    }

	    return this._personGrid;
	},



	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Listas de Distribuição'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				border: false,
				items: [
					this.getGroupPersonGrid(),
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
                            this.getPersonGrid(),
                            this.getControlPanel(),
                            this.getPersonSelectedGrid()
                        ]
                    }
				]
			}
		);

		edocs.protocolo.GroupPersonManage.superclass.constructor.call(this, cfg);
		this.observeGroupPerson();
	}
});
