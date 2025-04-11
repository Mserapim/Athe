/**
 *
 **/

Ext._define('rh.gfp.paycheck.PayCheckManageNew', {
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
			this.getEntriesGrid().enable();
			this.getEntriesGrid()._paycheck = this.paycheck();
			this.getEntriesGrid()._payrollStatus = selection[0].data.payroll_status;
			this.getEntriesGrid().setParam('contracheque', this.paycheck().pk);
			this.getEntriesGrid().setFilterProperty('contracheque', this.paycheck().pk, 100);
			this.getEntriesGrid().setFilterProperty('evento__tipo__in', ['P','D'], 101);
		}
		else{
			this.getEntriesGrid().disable();
			this.getEntriesGrid().getStore().removeAll();
			this.getEntriesGrid()._paycheck = null;
			this.getEntriesGrid()._payrollStatus = null;
			this.getEntriesGrid().setFilterProperty('contracheque', 0, 100, false);
		}
		this._grid.updateInfoToolBar();
	},

	getPayCheckGrid: function(cfg) {
		if(!this._grid){
			this._grid = Ext._create('rh.gfp.paycheck.PayCheckGridNew', {
                period: cfg.period,
                payrollType: cfg.payrollType,
                complement: cfg.complement,
				region: 'center',
				hideColumns: [
					'unicode',
					// 'folha_unicode',
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

	getEntriesGrid: function(cfg) {
		if(!this._entries)
			this._entries = Ext._create('rh.gfp.paycheck.EntriesGrid', {
				region: 'south',
				gridAutoLoad: false,
				disabled: true,
				split: true,
				// allEvent: this,
				flex: 0.5,
				height: 400,
				hideColumns:[
				],
				baseParams: {start: 0, limit: 100},
                viewConfig: {
                    stripeRows: false,
                    getRowClass: function(record, index, rowParams, store){
						const eventStyles = {
							'I': 'info-entry',
							'P': 'prov-entry',
							'D': 'desc-entry'
						};
						style = eventStyles[record.data.event_type]
                        style += (record.data.status == 'NC'? ' nc-entry': '');
                        return style;
                    }
                },
			});

			this._entries.getSelectionModel().on({
				scope: this._entries,
				selectionchange: function(grid){
					grid.grid.updateInfoToolBar();
					return true
				},
			});

		return this._entries;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Contracheque - Lançador de Eventos'
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
					this.getPayCheckGrid(cfg),
					this.getEntriesGrid(cfg),
				]
			}
		);

		rh.gfp.paycheck.PayCheckManageNew.superclass.constructor.call(this, cfg);
		this.observePayCheck();
	}
});
