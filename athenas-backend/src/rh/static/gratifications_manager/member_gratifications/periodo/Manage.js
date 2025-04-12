 Ext._define('rh.gratifications_manager.member_gratifications.periodo.Manage', {
	extend: 'toolkit.widget.TabPanel',

	event: function(cfg, value, dispatch){
		dispatch = core.nullValue(dispatch, true);
		if(value !== undefined){
			this._event = value;

			if(dispatch) this.observeMembrosConsolidadosEvent(cfg);
		}
		else
			return this._event;
	},

	observeMembrosConsolidadosEvent: function(cfg){
		var selection = this.getPeriodoGratMembrosGrid().getSelectionModel().getSelections();
		if(this.event() && selection.length == 1){
			this.getMembrosConsolidadosGrid(cfg).enable();
			this.getMembrosConsolidadosGrid(cfg)._event = this.event();

			this.getMembrosConsolidadosGrid(cfg)._toolbar.items.items.forEach(function(item){
				if(item.text == 'Filtrar Verba'){
					item.menu.items.items.forEach(function(itemFiltroVerba){
						if(itemFiltroVerba.text == 'Todos'){
							itemFiltroVerba.setChecked(true);
						}else{
							itemFiltroVerba.setChecked(false);
						}
					});
				}
			});

			this.getMembrosConsolidadosGrid(cfg).setParam('periodo', this.event().pk);
			this.getMembrosConsolidadosGrid(cfg).setFilterProperty('periodo', this.event().pk, 100, false);
            this.getMembrosConsolidadosGrid(cfg).removeFilterProperty('evento__numero__in', 1, true);

		}
		else{
			this.getMembrosConsolidadosGrid(cfg).disable();
			this.getMembrosConsolidadosGrid(cfg).getStore().removeAll();
			this.getMembrosConsolidadosGrid(cfg).setFilterProperty('periodo', 0, 100, false);
            this.getMembrosConsolidadosGrid(cfg).removeFilterProperty('evento__numero__in', 1, false);
		}
    },

	getPeriodoGratMembrosGrid: function(cfg) {
		if(!this._eventGrid){
			this._eventGrid = Ext._create('rh.gratifications_manager.member_gratifications.periodo.Grid', {
				region: 'north',
				split: true,
				gridAutoLoad: true,
				height: 200,
				sm: new Ext.grid.RowSelectionModel({singleSelect: false}),
				doubleClickHandler: function(grid) { },
			});

			this._eventGrid.getSelectionModel().on({
				scope: this,
				beforerowselect: function(eventGrid){
					return true
				},
				rowselect: function(eventGrid, index, record){
					this.event(cfg, record.data);
				},
				rowdeselect: function(eventGrid, index, record){
					this.event(cfg, null);
				},
			});
	
			this._eventGrid.getStore().on({
				scope: this,
				beforeload: function(st, options){
					rec = this._eventGrid.getSelectionModel().getSelected();
					this._eventGrid._lastEvent = rec? rec.data.pk: null;
				},
				load: function(st, records, options){
					if(!records.length)
						this.event(null);
				}
			});
		}

		return this._eventGrid;
	},

	getMembrosConsolidadosGrid: function(cfg) {
		if(!this._membrosConsolidadosGrid)
			this._membrosConsolidadosGrid = Ext._create('rh.gratifications_manager.member_gratifications.membros_consolidados.Grid', {
				gridAutoLoad: false,
				disabled: true,
				flex: 1.0,
				border: false,
				eventos: cfg.eventos,
			});

			this._membrosConsolidadosGrid.getSelectionModel().on({
                scope: this,
                rowselect: function (sm, index, record) {
                    this.observeGratificacoesEvent(record.get('pk'));
                },
                rowdeselect: function (sm) {
                    this.observeGratificacoesEvent(null);
                }

            });

		return this._membrosConsolidadosGrid;
	},

	observeGratificacoesEvent: function(gratMembroId){
		if(gratMembroId != null){
			this.getGratificacoesGrid().enable();
			this.getGratificacoesGrid().setFilterProperty('grat_membro_id', gratMembroId, 100, true);
		}
		else{
			this.getGratificacoesGrid().disable();
			this.getGratificacoesGrid().getStore().removeAll();
			this.getGratificacoesGrid().setFilterProperty('grat_membro_id', 0, 100, false);
		}
    },

	getGratificacoesGrid: function(cfg) {
		if(!this._gratificacoesGrid)
			this._gratificacoesGrid = Ext._create('rh.gratifications_manager.member_gratifications.gratificacoes.Grid', {
				gridAutoLoad: false,
				disabled: true,
				flex: 1.0,
				border: false,
				hideColumns:[],
			});

		return this._gratificacoesGrid;
	},

	getControlPanel: function () {
        if (!this._controlPanel)
            this._controlPanel = Ext._create('Ext.Panel', {
                width: 15,
                frame: true,
                layout: 'vbox',
                bodyStyle: {
                    'border-top': 0,
                    'border-bottom': 0
                },
            });
        return this._controlPanel;
    },

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gratificações de Membros'
			}
		);

		Ext.apply(
			cfg,
			{
				region: 'center',
                layout: 'border',
                border: false,
                scope: this,
                items: [
                    this.getPeriodoGratMembrosGrid(cfg),
                    {
                        region: 'center',
                        layout: 'hbox',
                        minHeight: 150,
                        scope: this,
                        bodyStyle: {
                            'border-left': 0,
                            'border-right': 0
                        },
                        layoutConfig: {
                            align: 'stretch'
                        },
                        items: [
                            this.getMembrosConsolidadosGrid(cfg),
                            this.getControlPanel(),
                            this.getGratificacoesGrid(),
                        ]
                    }
                ],
			}
		);

		rh.gratifications_manager.member_gratifications.periodo.Manage.superclass.constructor.call(this, cfg);
	}
});
