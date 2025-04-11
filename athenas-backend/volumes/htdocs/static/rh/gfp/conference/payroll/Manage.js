Ext._define('rh.gfp.conference.payroll.Manage', {
	extend: 'toolkit.widget.TabPanel',

	paycheck: function(value, dispatch){
		dispatch = core.nullValue(dispatch, true);
		if(value !== undefined){
			this._paycheck = value;

			if(dispatch) this.observePayCheck();
		}
		else
			return this._paycheck;
	},

	observePayCheck: function() {
		var selection = this.getPayCheckGrid().getSelectionModel().getSelections();
		if(this.paycheck() && selection.length == 1){
			this.getEntriesPreviousGrid().enable();
			this.getEntriesPreviousGrid()._paycheck = this.paycheck();
			this.getEntriesPreviousGrid()._payroll = this.getPayCheckGrid().payroll();
			this.getEntriesPreviousGrid().setParam('contracheque', this.paycheck().previous_paycheck);
			this.getEntriesPreviousGrid().setFilterProperty('contracheque', this.paycheck().previous_paycheck, 100);

            this.getEntriesCurrentGrid().enable();
			this.getEntriesCurrentGrid()._paycheck = this.paycheck();
			this.getEntriesCurrentGrid()._payroll = this.getPayCheckGrid().payroll();
			this.getEntriesCurrentGrid().setParam('contracheque', this.paycheck().pk);
			this.getEntriesCurrentGrid().setFilterProperty('contracheque', this.paycheck().pk, 100);
		}
		else{
			this.getEntriesPreviousGrid().disable();
			this.getEntriesPreviousGrid().getStore().removeAll();
			this.getEntriesPreviousGrid()._paycheck = null;
			this.getEntriesPreviousGrid()._payroll = null;
			this.getEntriesPreviousGrid().setFilterProperty('contracheque', 0, 100, false);

            this.getEntriesCurrentGrid().disable();
			this.getEntriesCurrentGrid().getStore().removeAll();
			this.getEntriesCurrentGrid()._paycheck = null;
			this.getEntriesCurrentGrid()._payroll = null;
			this.getEntriesCurrentGrid().setFilterProperty('contracheque', 0, 100, false);
		}
		this._grid.updateInfoToolBar();  
	},


    observeConference: function () {
        var value = this.conference();
        if (value) {
            this.getPayCheckGrid().enable();
            this.getPayCheckGrid().setParam('folha',value);
            this.getPayCheckGrid().setFilterProperty('folha', value, 1000);

        } else {
            this.getPayCheckGrid().disable();
            this.getPayCheckGrid().setFilterProperty('folha', 0, 1000,false);
            this.getPayCheckGrid().getStore().removeAll();


        }
    },

    conference: function (value, observe) {
        observe = (observe === undefined ? true : observe);

        if (value !== undefined) {
            this._conference = value;

            if (observe)
                this.observeConference();
        }
        return this._conference;
    },

	getPayCheckGrid: function() {
		if(!this._grid){
			this._grid = Ext._create('rh.gfp.conference.payroll.PayCheckGrid', {
				region: 'south',
				gridAutoLoad: false,
                layout: 'fit',
                minHeight: 100,
                height: 150,
                split: true,
                hideColumns: [
					'unicode',
					'folha_unicode', 
					'data_admissao', 
					'referencia_salarial_eletivo_unicode',
					'referencia_efetivo_cache',
					'cargo_eletivo_unicode',
					'referencia_salarial_comissao_unicode',
					'referencia_salarial_efetivo_unicode',
					'situacao_funcional',
					'situacao_previdenciaria',
					'cargo_comissao_unicode',
					'modified_by_unicode',
					'referencia_eletivo_cache',
					'modified_at',
					'created_by_unicode',
					'status_display',
					'cargo_efetivo_unicode',
					'base_previdenciaria',
					'total_bruto',
					'referencia_comissao_cache',
					'dependentes_sf',
					'created_at',
					'lotacao_unicode',
				],
				sm: new Ext.grid.RowSelectionModel({singleSelect: false}),
			});

			this._grid.getSelectionModel().on({
				scope: this,
				beforerowselect: function(grid){
					// console.debug('BEFORESELECT');
					return true
				},
				rowselect: function(grid, index, record) {
					this.paycheck(record.data);
					// console.debug('DESELECT');
				},
				rowdeselect: function(grid, index, record){
					this.paycheck(null);
				}
			});

			this._grid.getStore().on({
				scope: this,
				beforeload: function(st, options){
					// this.paycheck(null);
					rec = this._grid.getSelectionModel().getSelected();
					this._grid._lastPaycheck = rec? rec.data.pk: null;
					// console.debug('BEFORELOAD..'+this._grid._lastPaycheck);
				},
				load: function(st, records, options){
					this._grid.selectRowByPk(this._grid._lastPaycheck);
					if(!records.length)
					    this.paycheck(null);

				}
			});
		}

		return this._grid;
	},

	getEntriesCurrentGrid: function(cfg) {
		if(!this._entriesCurrent)
			this._entriesCurrent = Ext._create('rh.gfp.conference.payroll.EntriesGrid', {
				region: 'south',
				gridAutoLoad: false,
				disabled: true,
				split: true,
				flex: 0.5,
				columnAction: false,
                minHeight: 100,
                height: 150,
				hideColumns:[
					'valor',
					'patronal',
					'correct_patronal',
					'valor_base',
					'icons_previous'
				],
				baseParams: {start: 0,grid: this.getPayCheckGrid(),EntriesGrid:this.getEntriesPreviousGrid(),limit: 100},
                viewConfig: { 
                    stripeRows: false, 
                    getRowClass: function(record, index, rowParams, store){
                        style = (record.data.event_type == 'P'? 'prov-entry': 'desc-entry'); 
                        style += (record.data.status == 'NC'? ' nc-entry': ''); 
                        return style;
                    } 
                },				
			});

			this._entriesCurrent.getSelectionModel().on({
				scope: this._entriesCurrent,
				selectionchange: function(grid){
					grid.grid.updateInfoToolBar();
					return true
				},
			});

		return this._entriesCurrent;
	},

    getEntriesPreviousGrid: function(cfg) {
		if(!this._entriesPrevious)
			this._entriesPrevious = Ext._create('rh.gfp.conference.payroll.EntriesGrid', {
				region: 'south',
				gridAutoLoad: false,
				disabled: true,
				split: true,
				// allEvent: this,
				flex: 0.5,
                minHeight: 100,
                height: 150,
				columnAction: false,
				hideColumns:[
					'valor',
					'patronal',
					'correct_patronal',
					'valor_base',
					'icons',
				],
				baseParams: {start: 0,grid: this.getPayCheckGrid(), limit: 100},
                viewConfig: { 
                    stripeRows: false, 
                    getRowClass: function(record, index, rowParams, store){
                        style = (record.data.event_type == 'P'? 'prov-entry': 'desc-entry'); 
                        style += (record.data.status == 'NC'? ' nc-entry': ''); 
                        return style;
                    } 
                },				
			});

			this._entriesPrevious.getSelectionModel().on({
				scope: this._entriesPrevious,
				selectionchange: function(grid){
					grid.grid.updateInfoToolBar();
					return true
				},
			});

		return this._entriesPrevious;
	},

    getConferenceGrid: function (cfg) {
        if (!this._conferenceGrid) {
            this._conferenceGrid = Ext._create('rh.gfp.conference.payroll.ConferenceGrid', {
                region: 'north',
                minHeight: 200,
                height: 250,
                split: true,
                gridAutoLoad: true
            });

            this._conferenceGrid.getSelectionModel().on({
                scope: this,
                rowselect: function (sm, index, record) {
                    this.conference(record.get('payroll'));
                },
                rowdeselect: function (sm) {
                    this.conference(null);
                }
            });

            this._conferenceGrid.getStore().on({
                scope: this,
                load: function () {
                    this.observeConference();
                }
            });


        }

        return this._conferenceGrid;
    },

    getSplitGrid: function () {
        if (!this._middleGrid)
            this._middleGrid = Ext._create('Ext.Panel', {
                layout: 'hbox',
                border: false,
                region: 'south',
                height: 350,
                layoutConfig: {
                    align: 'stretch',
                    border: false
                },
                defaults: {
                    flex: 1.0,
                    layout: 'fit'
                },
                items: [
                    {
                        items: [
                            this.getEntriesPreviousGrid()
                        ]
                    },
                    {
                        items: [
                            this.getEntriesCurrentGrid()
                        ]
                    }
                ]
            });

        return this._middleGrid;
    },

    getPayCheckGridPanel: function (cfg) {
        if (!this._paycheckPanel)
            this._paycheckPanel = Ext._create('Ext.Panel', {
                layout: 'hbox',
                border: false,
                region: 'center',
                height: 200,
                layoutConfig: {
                    align: 'stretch',
                    border: false
                },
                defaults: {
                    flex: 1.0,
                    layout: 'fit'
                },
                items: [
                    {
                        items: [
                            this.getPayCheckGrid()
                        ]
                    }
                ]
            });

        return this._paycheckPanel;
    },

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Conferência de Folha'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				defaults: {
					split: true,
					// bodyStyle: 'padding:15px'
				},				
				items:[
                    this.getConferenceGrid(cfg),
                    this.getPayCheckGridPanel(cfg),
                    this.getSplitGrid(cfg),


				]
			}
		);

		rh.gfp.conference.payroll.Manage.superclass.constructor.call(this, cfg);
		this.observePayCheck();
	}
});
