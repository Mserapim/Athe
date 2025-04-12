Ext._define('judicial.RequestCollaborationPanel', {
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
            this.getRequestCollaborationGrid().enable();
            this.getRequestCollaborationGrid().setFilterProperty('lawsuit', value, 1000);
            // TODO: Filtrar por worklocations do usuario ou pela PF deste
        } else  {
            this.getRequestCollaborationGrid().disable();
            this.getRequestCollaborationGrid().setFilterProperty('lawsuit', 0, 1000, false);
            this.getRequestCollaborationGrid().getStore().removeAll();
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
            else
                this._procedureGrid.setFilterProperty('requestcollaboration', null, -1000, false);
            if (cfg.params.location)
                this._procedureGrid.setFilterProperty('location', cfg.params.location, 1002, false);

            this._procedureGrid.getStore().reload();
        }

        return this._procedureGrid;
    },

    getRequestCollaborationGrid: function(cfg) {
        if(!this._requestCollaborationGrid) {
            this._requestCollaborationGrid = Ext._create('judicial.requestcollaboration.Grid', {
                title: 'Requisições de colaboração',
                region: 'center',
                configOrderToolBar: [],
                hideActions: ['remove', 'edit', 'copy'],
                allowRemove: false,
                allowUpdate: false,
                gridAutoLoad: false,
                hideColumns: ['unicode', 'lawsuit_unicode']
            });

        }

        return this._requestCollaborationGrid;
    },

    constructor: function(cfg) {
        cfg = cfg || {};


        Ext.applyIf(cfg, {
           title: 'Gestor de Colaboração'
        });

        Ext.apply(cfg, {
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
                    items: this.getRequestCollaborationGrid(cfg),
                }
            ]
        });

        judicial.RequestCollaborationPanel.superclass.constructor.call(this, cfg);
    }
});
