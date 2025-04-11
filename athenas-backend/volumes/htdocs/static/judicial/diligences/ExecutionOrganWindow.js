
Ext._define('judicial.diligences.ExecutionOrganWindow', {
    extend: 'Ext.Window',

    getExecutionOrgan: function(cfg) {
    	if(!this._executionOrgan) {
            this._executionOrgan = Ext._create('judicial.diligences.ExecutionOrgan', {
                title: 'Diligências',
                gridAutoLoad: false
            });

            if(cfg.params) {
                if (cfg.params.lawsuit)
                    this._executionOrgan.getDiligenceGrid({gridAutoLoad: false}).setFilterProperty(
                        'part__lawsuit',
                        cfg.params.lawsuit,
                        101,
                        false
                    );

                if (cfg.params.type_lawsuit)
                    this._executionOrgan.getDiligenceGrid({gridAutoLoad: false}).setFilterProperty(
                        'part__lawsuit__type_lawsuit',
                        cfg.params.type_lawsuit,
                        102,
                        false
                    );

                if (cfg.params.location)
                    this._executionOrgan.getDiligenceGrid({gridAutoLoad: false}).setFilterProperty(
                        'part__lawsuit__location',
                        cfg.params.location,
                        103,
                        false
                    );
            }
        }

        return this._executionOrgan;
    },

    getLawsuitProceduralMovements: function(cfg) {
        if(!this._proceduralMovements) {
            this._proceduralMovements = Ext._create('judicial.LawsuitProceduralMovementsPanel', {
                title: 'Tramitações',
                params: cfg.params,
                classLawsuitGrid: cfg.classLawsuitGrid
            });
        }

        return this._proceduralMovements;
    },

    getCollaborationGrid: function(cfg) {
        if(!this._requestCollaboration) {
            this._requestCollaboration = Ext._create('judicial.requestcollaboration.Grid', {
                title: 'Colaborações',
                configOrderToolBar: [],
                hideActions: ['remove', 'edit', 'copy'],
                allowRemove: false,
                allowUpdate: false,
                gridAutoLoad: false,
                hideColumns: ['unicode', 'lawsuit_unicode']
            });

            if(cfg.params && cfg.params.location)
                this._requestCollaboration.setFilterProperty('origin_location', cfg.params.location, 1000, false);
            if(cfg.params && cfg.params.lawsuit)
                this._requestCollaboration.setFilterProperty('lawsuit', cfg.params.lawsuit, 1001, false);
            this._requestCollaboration.getStore().reload();
        }

        return this._requestCollaboration;
    },

    getRecomendationPanel: function(cfg) {
    	if(!this._recomendationPanel) {
            this._recomendationPanel = Ext._create('judicial.parts.RecomendationTabPanel', {
                title: 'Recomendações',
                gridAutoLoad: false
            });

            if(cfg.params) {
                if (cfg.params.lawsuit)
                    this._recomendationPanel.getRecomendationGrid({gridAutoLoad: false}).setFilterProperty(
                        'lawsuit',
                        cfg.params.lawsuit,
                        101,
                        false
                    );

                if (cfg.params.type_lawsuit)
                    this._recomendationPanel.getRecomendationGrid({gridAutoLoad: false}).setFilterProperty(
                        'lawsuit__type_lawsuit',
                        cfg.params.type_lawsuit,
                        102,
                        false
                    );

                if (cfg.params.location)
                    this._recomendationPanel.getRecomendationGrid({gridAutoLoad: false}).setFilterProperty(
                        'lawsuit__location',
                        cfg.params.location,
                        103,
                        false
                    );
            }
        }

        return this._recomendationPanel;
    },

    getTacPanel: function(cfg) {
        if(!this._tacPanel) {
            this._tacPanel = Ext._create('judicial.tac.FollowDeadlineTAC', {
                title: 'TAC',
                gridAutoLoad: false
            });

            if(cfg.params) {
                if (cfg.params.lawsuit)
                    this._tacPanel.getManagementTacGrid().setFilterProperty(
                        'lawsuit__pk',
                        cfg.params.lawsuit,
                        101,
                        false
                    );

                if (cfg.params.location)
                    this._tacPanel.getManagementTacGrid().setFilterProperty(
                        'lawsuit__location',
                        cfg.params.location,
                        103,
                        false
                    );

            }

            this._tacPanel.getManagementTacGrid().getStore().reload();

        }

        return this._tacPanel;
    },

    requestExternalAccess: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._requestExternalAccess = value;

            if(dispatch)
                this.requestExternalAccessObserve();
        }

        return this._requestExternalAccess;
    },

    requestExternalAccessObserve: function() {
        var value = this.requestExternalAccess();

        if(value) {
            this.getRequestExternalAccessTilePanel().setPageContent(value.get('rendered_request'));
        }
        else {
            this.getRequestExternalAccessTilePanel().setPageContent(null);
        }
    },

    getRequestExternalAccessGrid: function(cfg) {
        if(!this._requestExternalAccessGrid) {
            this._requestExternalAccessGrid = Ext._create('judicial.requestexternalaccess.Grid', {
                configOrderToolBar: ['search', '->', 'download'],
                region: 'center',
                minWidth: 600,
                gridAutoLoad: false
            });

            var grid = this._requestExternalAccessGrid;

            grid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sel) {
                    var selection = sel.getSelections();

                    if(selection.length > 0)
                        this.requestExternalAccess(selection[0]);
                    else
                        this.requestExternalAccess(null);
                }
            });

            grid.setFilterProperty('lawsuit__location', ((cfg.params || {}).location || 0), 1001, false);
            grid.addFilterProperty('state__in', [1], 100, false);
            if((cfg.params || {}).lawsuit)
                grid.setFilterProperty('lawsuit', (cfg.params || {}).lawsuit, 1002, false);

            grid.getStore().reload();
        }

        return this._requestExternalAccessGrid;
    },

    getRequestExternalAccessTilePanel: function(cfg) {
        if(!this._requestExternalAccessTilePanel)
            this._requestExternalAccessTilePanel = Ext._create('core.TilePagePanel', {
                xtype: 'panel',
                region: 'east',
                width: 840,
                split: true
            });

        return this._requestExternalAccessTilePanel;
    },

    getRequestExternalAccess: function(cfg) {
        if(!this._requestExternalAccess)
            this._requestExternalAccess = Ext._create('Ext.Panel', {
                title: 'Requisições de Acesso',
                layout: 'border',
                border: false,
                items: [
                    this.getRequestExternalAccessGrid(cfg),
                    this.getRequestExternalAccessTilePanel(cfg)
                ]
            });

        return this._requestExternalAccess;
    },

    getTabPanel: function(cfg) {
        if(!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                border: false,
                frame: false,
                activeTab: 0,
                height: cfg.height - 32,
                items: [
                    this.getMainDashboardPanel(cfg),
                    this.getExecutionOrgan(cfg),
                    this.getLawsuitProceduralMovements(cfg),
                    this.getCollaborationGrid(cfg),
                    this.getRecomendationPanel(cfg),
                    this.getTacPanel(cfg),
                    this.getRequestExternalAccess(cfg)
                ]
            });

        return this._tabPanel;
    },

    getMainDashboardPanel: function(cfg) {
        if(!this._mainDashboardPanel) {
            var defaultFilters = [
                {
                    property: 'part__lawsuit__location',
                    value: cfg.params.location,
                    stage: 0
                }
            ];

            var defaultFiltersRecomendation = [
                {
                    property: 'lawsuit__location',
                    value: cfg.params.location,
                    stage: 0
                }
            ];

            var defaultFiltersCollaboration = [];

            if(cfg.params.lawsuit) {
                defaultFilters.push({
                    property: 'part__lawsuit',
                    value: cfg.params.lawsuit,
                    stage: 1
                });
            }

            var defaultCallback = {
                scope: this,
                fn: function(counter) {
                    var tab = this.getExecutionOrgan();
                    var targetGrid = tab.getDiligenceGrid();
                    var managePanel = this.getTabPanel();

                    managePanel.activate(tab);
                    targetGrid.setFilter(counter.filter, true);
                }
            };

            var callbackRecomendation = {
                scope: this,
                fn: function(counter) {
                    var tab = this.getRecomendationPanel();
                    var targetGrid = tab.getRecomendationGrid();
                    var managePanel = this.getTabPanel();

                    managePanel.activate(tab);
                    targetGrid.setFilter(counter.filter, true);
                }
            };

            var callbackCollaboration = {
                scope: this,
                fn: function(counter) {
                    var tab = this.getCollaborationGrid();
                    var targetGrid = tab;
                    var managePanel = this.getTabPanel();

                    managePanel.activate(tab);
                    targetGrid.setFilter(counter.filter, true);
                }
            };

            this._mainDashboardPanel = Ext._create('judicial.dashboard.Panel', {
                title: 'Quadro',
                columns: 2,
                cellHeight: (Number.parseInt(cfg.height) / 2),
                autoScroll: true,
                panels: [
                    {
                        title: 'Minhas diligências',
                        rest: 'judicial.diligences.ExecutionOrganRestful',
                        width: (Number.parseInt(cfg.width) / 2)- 20,
                        counters: [
                            {
                                title: 'Diligências aguardando respostas',
                                name: 'row1',
                                callback: defaultCallback,
                                filter: defaultFilters.concat([
                                    {
                                        property: 'delivery_status',
                                        value: 9,
                                        stage: 2
                                    }
                                ])
                            },
                            {
                                title: 'Diligências sem resposta no prazo',
                                name: 'row2',
                                callback: defaultCallback,
                                filter: defaultFilters.concat([
                                    {
                                        property: 'delivery_status',
                                        value: 10,
                                        stage: 2
                                    }
                                ])
                            },
                            {
                                title: 'Diligências respondidas',
                                name: 'row3',
                                callback: defaultCallback,
                                filter: defaultFilters.concat([
                                    {
                                        property: 'delivery_status',
                                        value: 99,
                                        stage: 2
                                    },
                                    {
                                        property: 'has_manifestations__signed_by',
                                        value: null,
                                        stage: -1
                                    }
                                ])
                            },
                            {
                                title: 'Diligências finalizadas',
                                name: 'row4',
                                callback: defaultCallback,
                                filter: defaultFilters.concat([
                                    {
                                        property: 'delivery_status',
                                        value: 99,
                                        stage: 2
                                    }
                                ])
                            },
                            {
                                title: 'Diligências devolvidas sem êxito',
                                name: 'row5',
                                callback: defaultCallback,
                                filter: defaultFilters.concat([
                                    {
                                        property: 'delivery_status',
                                        value: 8,
                                        stage: 2
                                    }
                                ])
                            },
                            {
                                title: 'Diligências em processo de entrega',
                                name: 'row6',
                                callback: defaultCallback,
                                filter: defaultFilters.concat([
                                    {
                                        property: 'delivery_status__in',
                                        value: [2, 3, 4, 7],
                                        stage: 2
                                    }
                                ])
                            },
                            {
                                title: 'Diligências em edição',
                                name: 'row7',
                                callback: defaultCallback,
                                filter: defaultFilters.concat([
                                    {
                                        property: 'delivery_status__in',
                                        value: [1],
                                        stage: 2
                                    }
                                ])
                            }
                        ]
                    },
                    {
                        title: 'Minhas Recomendações',
                        rest: 'judicial.parts.RecomendationRestful',
                        width: (Number.parseInt(cfg.width) / 2)- 20,
                        counters: [
                            {
                                title: 'Recomendações em andamento',
                                name: 'row1',
                                callback: callbackRecomendation,
                                filter: defaultFiltersRecomendation.concat([
                                    {
                                        property: 'finished_by__isnull',
                                        value: true,
                                        stage: 2
                                    },
                                    {
                                        property: 'signed_by__isnull',
                                        value: false,
                                        stage: 3
                                    },
                                    {
                                        property: 'remaining_days__gte',
                                        value: 0,
                                        stage: 4
                                    }
                                ])
                            },
                            {
                                title: 'Recomendações cumpridas',
                                name: 'row2',
                                callback: callbackRecomendation,
                                filter: defaultFiltersRecomendation.concat([
                                    {
                                        property: 'finished_by__isnull',
                                        value: false,
                                        stage: 2
                                    }
                                ])
                            },
                            {
                                title: 'Recomendações em atraso',
                                name: 'row3',
                                callback: callbackRecomendation,
                                filter: defaultFiltersRecomendation.concat([
                                    {
                                        property: 'finished_by__isnull',
                                        value: true,
                                        stage: 2
                                    },
                                    {
                                        property: 'signed_by__isnull',
                                        value: false,
                                        stage: 3
                                    },
                                    {
                                        property: 'remaining_days__lt',
                                        value: 0,
                                        stage: 4
                                    }
                                ])
                            }
                        ]
                    },
                    {
                        title: 'Colaborações solicitadas',
                        rest: 'judicial.requestcollaboration.Restful',
                        width: (Number.parseInt(cfg.width) / 2)- 20,
                        counters: [
                            {
                                title: 'Pelo meu departamento (ativas)',
                                name: 'row1',
                                callback: callbackCollaboration,
                                filter: defaultFiltersCollaboration.concat([
                                    {
                                        property: 'origin_location',
                                        value: cfg.params.location,
                                        stage: 2
                                    },
                                    {
                                        property: 'canceled_by',
                                        value: null,
                                        stage: 3
                                    }
                                ])
                            },
                            {
                                title: 'Pelo meu departamento (inativas)',
                                name: 'row2',
                                callback: callbackCollaboration,
                                filter: defaultFiltersCollaboration.concat([
                                    {
                                        property: 'origin_location',
                                        value: cfg.params.location,
                                        stage: 2
                                    },
                                    {
                                        property: 'canceled_by',
                                        value: null,
                                        stage: -3
                                    }
                                ])
                            },
                            {
                                title: 'Ao meu departamento (ativas)',
                                name: 'row3',
                                callback: callbackCollaboration,
                                filter: defaultFiltersCollaboration.concat([
                                    {
                                        property: 'requestcollaborationgeneralorgan__general_organ',
                                        value: cfg.params.location,
                                        stage: 2
                                    },
                                    {
                                        property: 'canceled_by',
                                        value: null,
                                        stage: 3
                                    }
                                ])
                            },
                            {
                                title: 'Ao meu departamento (inativas)',
                                name: 'row4',
                                callback: callbackCollaboration,
                                filter: defaultFiltersCollaboration.concat([
                                    {
                                        property: 'requestcollaborationgeneralorgan__general_organ',
                                        value: cfg.params.location,
                                        stage: 2
                                    },
                                    {
                                        property: 'canceled_by',
                                        value: null,
                                        stage: -3
                                    }
                                ])
                            },
                            {
                                title: 'Para mim (ativas)',
                                name: 'row5',
                                callback: callbackCollaboration,
                                filter: defaultFiltersCollaboration.concat([
                                    {
                                        property: 'requestcollaborationperson__person',
                                        value: '__USER_PERSON__',
                                        stage: 2
                                    },
                                    {
                                        property: 'canceled_by',
                                        value: null,
                                        stage: 3
                                    }
                                ])
                            },
                            {
                                title: 'Para mim (inativas)',
                                name: 'row6',
                                callback: callbackCollaboration,
                                filter: defaultFiltersCollaboration.concat([
                                    {
                                        property: 'requestcollaborationperson__person',
                                        value: '__USER_PERSON__',
                                        stage: 2
                                    },
                                    {
                                        property: 'canceled_by',
                                        value: null,
                                        stage: -3
                                    }
                                ])
                            }
                        ]
                    }
                ]
            });
        }

        return this._mainDashboardPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
        	cfg,
        	{
        		title: 'Acompanhamento de Prazos',
        		closable: true,
				height: 700,
        		width: 800
        	}
        );

		Ext.apply(
			cfg,
			{
				items: [
                    this.getTabPanel(cfg)
                ]
			}
		);

		judicial.diligences.ExecutionOrganWindow.superclass.constructor.call(this, cfg);
    }
});
