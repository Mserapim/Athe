Ext._define('corregedoria.inspection.inspection.analyze_recommendation.Grid', {
    extend: 'core.RestfulGrid',

    rest: 'corregedoria.inspection.inspection.analyze_recommendation.Restful',
    restWindow: 'corregedoria.inspection.inspection.analyze_recommendation.Window',

    configOrderToolBar: ['search', '-'],

    getResponseWindow: function() {
        var selected = this.getSelectionModel().getSelected();
        if(selected) {
            Ext._create('corregedoria.inspection.inspection.analyze_recommendation.AnalyzeWindow', {
                values: {
                    recommendation: selected.data.pk,
                    recommendationsGrid: this,
                    reportcompliance: selected.data.reportcompliance_pending,
                    delayoftime: selected.data.delayoftime_pending,
                },
            }).show();
        }
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 70, renderer: core.rendererIconGrid, menuDisabled: true, },
                    {header: 'Recomendação', dataIndex: 'recommendation', id: 'autoExpandColumn', },
                    {header: 'Prazo', dataIndex: 'deadline_grid', width: 80, },
                ]
            );

        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                columnAction: false,
                doubleClickHandler: function() { this.getResponseWindow(); },
            }
        );
        corregedoria.inspection.inspection.analyze_recommendation.Grid.superclass.constructor.call(this, cfg);
    }
});
core.RestfulGrid.register(
    'corregedoria.inspection.inspection.analyze_recommendation.Restful',
    'corregedoria.inspection.inspection.analyze_recommendation.Grid'
);
