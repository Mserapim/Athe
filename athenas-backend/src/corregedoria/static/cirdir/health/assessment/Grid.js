Ext._define('corregedoria.cirdir.health.assessment.Grid', {
    extend: 'core.RestfulGrid',
    restWindow: 'corregedoria.cirdir.health.assessment.Window',

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'filterAssessment', 'search'],

    getColumnModel: function(cfg) {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 50, renderer: core.rendererIconGrid},
                    {header: 'Questionário', dataIndex: 'health_unicode', id: 'autoExpandColumn', hidden: ((cfg.hiddenColumns) || {}).health},
                    {header: 'Servidor/Membro', dataIndex: 'integrant_unicode', width: 250, hidden: ((cfg.hiddenColumns) || {}).employee},
                    {header: 'Avaliador', dataIndex: 'evaluator_unicode', width: 250, hidden: ((cfg.hiddenColumns) || {}).evaluator},
                ]
            );

        return this._columnModel;
    },

    getEvaluated: function() {
        this.showAllAssessment(false);
        this.addFilterProperty('signed_at__isnull', false, 100, true);
    },

    getNoEvaluated: function() {
        this.showAllAssessment(false);
        this.addFilterProperty('signed_at__isnull', true, 101, true);
    },

    showAllAssessment: function(reload) {
        this.removeFilterProperty('signed_at__isnull', 100, false);
        this.removeFilterProperty('signed_at__isnull', 101, reload);
    },

    getFilterAssessmentAction: function() {
        if(!this._filterAssessmentAction){
            this._filterAssessmentAction = new Ext.Button({
                xtype: 'button',
                text: 'Exibir',
                iconCls: 'icon-crgmpe icon-crgmpe-find',
                menu: [
                    {
                        text: 'Avaliados',
                        iconCls: 'icon-crgmpe icon-crgmpe-success',
                        scope: this,
                        handler: function() { this.getEvaluated(); }
                    },
                    {
                        text: 'Aguardando avaliação',
                        iconCls: 'icon-crgmpe icon-crgmpe-waiting',
                        scope: this,
                        handler: function() { this.getNoEvaluated(); }
                    },
                    '-',
                    {
                        text: 'Mostrar Todos',
                        iconCls: 'icon-crgmpe icon-crgmpe-list-papers',
                        scope: this,
                        handler: function() { this.showAllAssessment(true); }
                    },
                ]
            });
        }
        return this._filterAssessmentAction;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                columnAction: false
            }
        );
        corregedoria.cirdir.health.assessment.Grid.superclass.constructor.call(this, cfg);
    }

});

core.RestfulGrid.register(
    'corregedoria.cirdir.health.assessment.Restful',
    'corregedoria.cirdir.health.assessment.Grid'
);
