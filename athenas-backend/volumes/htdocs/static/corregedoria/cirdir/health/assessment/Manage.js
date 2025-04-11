Ext._define('corregedoria.cirdir.health.assessment.Manage', {
  extend: 'toolkit.widget.TabPanel',

    getEvaluatorAssessmentGrid: function(cfg) {
        if(!this._assessmentGrid) {
            this._assessmentGrid = Ext._create('corregedoria.cirdir.health.assessment.Grid', {
                region: 'north',
                configOrderToolBar: ['edit', '-', 'filterAssessment', '-', 'search'],
                height: Ext.getBody().getBox().height * 0.3,
                hiddenColumns: {
                    employee: false,
                    health: true,
                    evaluator: true,
                }
            });

            this._assessmentGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sel) {
                    var selected = sel.getSelected();
                    this.selectedItem(selected === undefined ? null : selected);
                }
            });

            this._assessmentGrid.getStore().on({
                scope: this,
                load: function() {
                    var selected = this._assessmentGrid.getSelectionModel().getSelected();
                    this.selectedItem(selected === undefined ? null : selected);
                }
            });

        }
        return this._assessmentGrid;
    },

    selectedItem: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._selectedItem = value;
            if(dispatch)
                this.observer();
        }

        return this._selectedItem;
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
            params: {pk: pk},
            method: 'GET',
            callback: function() {
                tile._readRenderTID = null;
                tile.mask.hide();
            },
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);

                if(rst.success) {
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


    observer: function() {
        var value = this.selectedItem();

        if(value) {
            this.renderPageContent(
                value.get('health'),
                this.getHealthEvaluationTilePanel(),
                'CIRDIRHealth',
                'rendered_evaluation'
            );

            this.renderPageContent(
                value.get('pk'),
                this.getAssessmentTilePanel(),
                'CIRDIRHealthAssessmentRestful',
                'rendered'
            );
        } else {
            this.getAssessmentTilePanel().setPageContent('');
            this.getHealthEvaluationTilePanel().setPageContent('');
        }
    },

    getEvaluatorPanel: function(cfg) {
        if(!this._evaluatorPanel)
            this._evaluatorPanel = Ext._create('Ext.Panel', {
                region: 'west',
                split: true,
                width: Ext.getBody().getBox().width * 0.55,
                minWidth: Ext.getBody().getBox().width * 0.3,
                maxWidth: Ext.getBody().getBox().width * 0.8,
                border: false,
                layout: 'border',
                items: [
                    this.getEvaluatorAssessmentGrid(cfg),
                    this.getAssessmentTilePanel(cfg)
                ]
            });

        return this._evaluatorPanel;
    },

    getAssessmentTilePanel: function(cfg) {
        if(!this._assessmentTilePanel)
            this._assessmentTilePanel = Ext._create('core.TilePagePanel', {
                region: 'center'
            });

        return this._assessmentTilePanel;
    },

    getHealthEvaluationTilePanel: function(cfg) {
        if(!this._healthEvaluationTile)
            this._healthEvaluationTile = Ext._create('core.TilePagePanel', {
                region: 'center',
            });

        return this._healthEvaluationTile;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};
        Ext.applyIf(
            cfg,
            {
                title: 'Painel de Avaliação'
            }
        );
        Ext.apply(
            cfg,
            {
                layout: 'border',
                border: false,
                items: [
                    this.getEvaluatorPanel(cfg),
                    this.getHealthEvaluationTilePanel(cfg)
                ],
            }
        );
        corregedoria.cirdir.health.assessment.Manage.superclass.constructor.call(this, cfg);
    },
});
