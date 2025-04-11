Ext._define('judicial.LawsuitProceduralMovementsPanel', {
    extend: 'Ext.Panel',

    procedure: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._procedure = value;

            if(dispatch)
                this.observeProcedure();
        }

        return this._procedure;
    },

    observeProcedure: function() {
        var value = this.procedure();

        if(value) {
            this.getLawsuitMovementGrid().enable();
            this.getLawsuitMovementGrid().setFilterProperty('out_court_lawsuit__pk', value, 1000);
        } else  {
            this.getLawsuitMovementGrid().disable();
            this.getLawsuitMovementGrid().setFilterProperty('out_court_lawsuit__pk', 0, 1000, false);
            this.getLawsuitMovementGrid().getStore().removeAll();
        }
    },

    getLawsuitProcedureGrid: function (cfg) {
        if(!this._procedureGrid) {
            this._procedureGrid = Ext._create(cfg.classLawsuitGrid, {
                title: 'Procedimentos',
                region: 'center',
                configOrderToolBar: ['search', '->'],
                gridConfig: {hiddenFilter: true},
                doubleClickHandler: function() {},
                columnAction: false,
                minWidth: 500,
                gridAutoLoad: false,
                onlyColumns: [
                    'cache_number',
                    'title',
                    'type_lawsuit_display'
                ],
            });

            this._procedureGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sm) {
                    var selection = sm.getSelections();

                    if(selection.length > 0)
                        this.procedure(selection[0].get('pk'));
                    else
                        this.procedure(null);
                }
            });

            this._procedureGrid.setFilterProperty('attached_lawsuit', null, 1000, false);
            if (cfg.params.lawsuit)
                this._procedureGrid.setFilterProperty('pk', cfg.params.lawsuit, 1001, false);
            if (cfg.params.location)
                this._procedureGrid.setFilterProperty('location', cfg.params.location, 1002, false);

            this._procedureGrid.getStore().reload();
        }

        return this._procedureGrid;
    },

    getLawsuitMovementGrid: function (cfg) {
        if(!this._movementGrid) {
            this._movementGrid = Ext._create('judicial.movementlog.Grid', {
                title: 'Movimentos',
                region: 'center',
                configOrderToolBar: ['search', '->'],
                gridConfig: {hiddenFilter: true},
                doubleClickHandler: function() {},
                columnAction: false,
                minWidth: 575,
                width: 575,
                disabled: true,
                gridAutoLoad: false,
                onlyColumns: [
                    'from_location_unicode',
                    'sended_by_unicode',
                    'sended_at',
                    'to_location_unicode',
                    'received_by_unicode',
                    'received_at'
                ],
            });
        }

        return this._movementGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Movimentações Procedimentais'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getLawsuitProcedureGrid(cfg),
                    {
                        xtype: 'panel',
                        region: 'east',
                        layout: 'border',
                        border: false,
                        minWidth: 575,
                        width: 750,
                        split: true,
                        items: this.getLawsuitMovementGrid(cfg)
                    }
                ]
            }
        );

        judicial.LawsuitProceduralMovementsPanel.superclass.constructor.call(this, cfg);
    }
});
