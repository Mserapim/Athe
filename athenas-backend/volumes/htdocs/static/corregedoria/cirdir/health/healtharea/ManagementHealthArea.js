Ext._define('corregedoria.cirdir.health.healtharea.ManagementHealthArea', {
    // extend: 'toolkit.widget.TabPanel',
    extend: 'Ext.Panel',

    getTabs: function() {
        if(!this._tabPanel) {
            this._tabPanel = Ext._create('Ext.TabPanel', {
                region: 'center',
                minHeight: 200,
                split:true,
                border: true,
                closable: false,
                disabled: true,
                activeTab: 0,
                items: [
                    this.getDetailTilePagePanel(),
                    this.getEvaluatorAssessmentGrid()
                ]
            });
        }
        return this._tabPanel;
    },

    getEvaluatorAssessmentGrid: function(cfg) {
        if(!this._assessmentGrid) {
            this._assessmentGrid = Ext._create('corregedoria.cirdir.health.assessment.Grid', {
                title: 'Pendência',
                region: 'center',
                configOrderToolBar: [],
                hideItemsToolbar:['add', 'edit', 'remove','download', '-'],
                doubleClickHandler: function(grid) {},
                hiddenColumns: {
                    health: true
                },
                storeDefaultRoute: 'management',
            });

            this._assessmentGrid.setFilterProperty('health', 0, 1000, false);
        }
        return this._assessmentGrid;
    },

    getHealthGrid: function(cfg) {
        if(!this._healthGrid) {
            this._healthGrid = Ext._create('corregedoria.cirdir.health.Grid', {
                region: 'center',
                allowUpdate: false,
                allowRemove: false,
                configOrderToolBar: ['-','FilterHealth', 'YearField', '-','search'],
                columnAction: false,
                hideItemsToolbar:['add', 'edit', 'remove','download', '-'],
                doubleClickHandler: function(grid) {},
                hiddenColumns: {
                    employee: false,
                    health: true
                }
            });

            this._healthGrid.setFilterProperty('controlinformation__employee__tipo', 'M', 999, false);
            this._healthGrid.setFilterProperty('controlinformation__authorization_health', true, 1000, false);

            this._healthGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sel) {
                    var selected = sel.getSelected();
                    this.healthSelected(selected === undefined ? null : selected, true);
                }
            });

            this._healthGrid.on({
                scope: this,
                yearselected: function(value) {
                    this._healthGrid.setFilterProperty('controlinformation__year', value, 1001, true);
                },
            });
        }
        return this._healthGrid;
    },

    autoSelectLastYear: function(cfg) {
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Buscando dados...'});
        var grid = this.getHealthGrid()
        mask.show();
        Ext.Ajax.request({
            scope: this,
            url: core.callAction('CIRDIRControlInformation', 'get_lastyear'),
            callback: function() {
                mask.hide();
            },
            success: function(request) {
                var rst = Ext.decode(request.responseText);
                if (rst.success == true) {
                    grid.getYearFieldAction().setValue(rst.lastyear);
                }
            },
            failure: function(request) {
                var rst = Ext.decode(request.responseText);
                Ext.Msg.show({
                    title: 'Erro ao buscar informações',
                    msg: rst.message,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            },
        });
    },

    healthSelected: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._healthSelected = value;

            if(dispatch)
                this.observer();

        }
        return this._healthSelected;
    },

    observer : function() {
        var value = this.healthSelected();

        if(value) {
            this.getTabs().enable();

            this.getEvaluatorAssessmentGrid().setFilterProperty('health', value.get('pk'), 1000);

            this.renderPageContent(
                value.get('pk'),
                this.getDetailTilePagePanel(),
                'CIRDIRHealth',
                'renderer_document'
            );

        } else {
            this.getTabs().disable();
            this.getEvaluatorAssessmentGrid().setFilterProperty('health', 0, 1000, false);
            this.getEvaluatorAssessmentGrid().getStore().removeAll({});
            this.getDetailTilePagePanel().setPageContent('');
        }
    },

    renderPageContent: function(pk, tile, controller, method) {
        if ( !tile.mask )
            tile.mask = new Ext.LoadMask(tile.getEl(), 'carregando informações...');

        if(tile._readRenderTID)
            Ext.Ajax.abort(tile._readRenderTID);

        tile.mask.show();
        tile.setPageContent('<p>Carregando conteúdo...</p>');
        tile._readRenderTID = Ext.Ajax.request({
            url: core.callAction(controller, method),
            params: {
                pk: pk,
                full: true
            },
            method: 'GET',
            callback: function() {
                tile._readRenderTID = null;
                tile.mask.hide();
            },
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);

                if(rst.success) {
                    tile.enable();
                    tile.setPageContent(rst.content);
                }
                else
                    tile.setPageContent([
                        '<p>Ocorreu um erro carregando o documento.</p>',
                        '<p>Mensagem: ' + rst.message + '</p>'
                    ].join(''));
            },
            failure: function(xhr) {
                tile.setPageContent('<p>Erro carregando informações do documento.</p>');
            }
        });
    },

    getEvaluatorGrid: function(cfg) {
        if(!this._evaluatorGrid) {
            this._evaluatorGrid = Ext._create('corregedoria.cirdir.evaluator.Grid', {
                region: 'south',
                split: true,
                border: false,
                height: 400,

            });
            this._evaluatorGrid.setHealthOriginGrid(this.getHealthGrid());
        }
        return this._evaluatorGrid;
    },

    getGridPanel: function() {
        if(!this._gridPanel)
            this._gridPanel = Ext._create('Ext.Panel', {
                region: 'center',
                width: '50%',
                split: true,
                border: false,
                layout: 'border',
                items: [
                    this.getHealthGrid(),
                    this.getEvaluatorGrid()
                ]
            });

        return this._gridPanel;
    },

    getDetailGridPanel: function() {
        if(!this._detailProtocolPanel)
            this._detailProtocolPanel = Ext._create('Ext.Panel', {
                region: 'east',
                width: '50%',
                split: true,
                border: false,
                layout: 'fit',
                items: [
                    this.getTabs()
                ]
            });

        return this._detailProtocolPanel;
    },


    getDetailTilePagePanel: function() {
        if(!this._datailProtocolTilePanel)
            this._datailProtocolTilePanel = Ext._create('core.TilePagePanel', {
                title: 'Questionário',
                disabled: true,
                region: 'center',
            });

        return this._datailProtocolTilePanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gerenciamento',
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getGridPanel(),
                    this.getDetailGridPanel(),
                ]
            }
        );

        corregedoria.cirdir.health.healtharea.ManagementHealthArea.superclass.constructor.call(this, cfg);

        this.on({
            scope: this,
            afterrender: function() {
                this.autoSelectLastYear();
            }
        });
    }
});
