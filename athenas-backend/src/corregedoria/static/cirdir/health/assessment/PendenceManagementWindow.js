Ext._define('corregedoria.cirdir.health.assessment.PendenceManagementWindow', {
    extend: 'Ext.Window',

    width: 1000,
    height: 600,

    getRightPanel: function(cfg) {
        if(!this._rightPanel)
            this._rightPanel = Ext._create('Ext.Panel', {
                height: this.height,
                width: this.width * 0.60,
                region: 'east',
                border: false,
                layout: 'border',
                items: [
                    this.getEvaluatorAssessmentGrid(cfg)
                ]
            });

        return this._rightPanel;
    },

    getCenterPanel: function(cfg) {
        if(!this._centerPanel)
            this._centerPanel = Ext._create('Ext.Panel', {
                height: this.height,
                width: this.width * 0.4,
                region: 'center',
                border: false,
                layout: 'border',
                items: [
                    this.getHealthGrid(cfg)
                ]
            });

        return this._centerPanel;
    },

    getHealthGrid: function(cfg) {
        if(!this._healthGrid) {
            this._healthGrid = Ext._create('corregedoria.cirdir.health.Grid', {
                region: 'center',
                params: {
                    closed_health: true,
                },
                configOrderToolBar: ['search', ],
                columnAction: false,
                hideItemsToolbar:['add', 'edit', 'remove','download', '-'],
                storeDefaultRoute: 'evaluation_pending_store',
                doubleClickHandler: function(grid) {},
            });
            this._healthGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sel) {
                    var selected = sel.getSelected();
                    this.healthSelected(selected === undefined ? null : selected);
                }
            });
        }
        return this._healthGrid;
    },

    getEvaluatorAssessmentGrid: function(cfg) {
        if(!this._assessmentGrid) {
            this._assessmentGrid = Ext._create('corregedoria.cirdir.health.assessment.Grid', {
                region: 'center',
                configOrderToolBar: ['search', ],
                hideItemsToolbar:['add', 'edit', 'remove','download', '-'],
                doubleClickHandler: function(grid) {},
                disabled: true,
                hiddenColumns: {
                    integrant: true,
                    health: true
                },
                storeDefaultRoute: 'management',
            });

            this._assessmentGrid.setFilterProperty('health', 0, 1000, false);
        }
        return this._assessmentGrid;
    },

    healthSelected: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch)

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
            this.getEvaluatorAssessmentGrid().enable();
            this.getEvaluatorAssessmentGrid().setFilterProperty('health', value.get('pk'), 1000, true);
        } else {
            this.getEvaluatorAssessmentGrid().disable();
            this.getEvaluatorAssessmentGrid().setFilterProperty('health', 0, 1000, false);
            this.getEvaluatorAssessmentGrid().removeAll({});
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(cfg, {
            title: 'Avaliações Pendentes',

            border: false,
            items: [
                this.getCenterPanel(cfg),
                this.getRightPanel(cfg)
            ],
            layout: {
                type: 'border'
            },
            buttons: [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() {
                        this.close();
                    }
                }
            ]
        });

        corregedoria.cirdir.health.assessment.PendenceManagementWindow.superclass.constructor.call(this, cfg);
    }

});
