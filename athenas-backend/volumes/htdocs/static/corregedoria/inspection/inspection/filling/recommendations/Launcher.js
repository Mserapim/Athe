
Ext._define('corregedoria.inspection.inspection.filling.recommendations.Launcher', {
    extend: 'Ext.Panel',

    getRecommendationsGrid: function(cfg) {
        if(!this._recommendationsGrid) {
            this._recommendationsGrid = Ext._create('corregedoria.inspection.inspection.filling.recommendations.Grid', {
                region: 'center',
                layout: 'form',
                border: true,
                height: 530,
                gridAutoLoad: true,
                columnAction: false,
                hideItemsToolbar:['edit', 'download', '-', 'search'],
                params: {inspection: cfg.values.inspection_id},
            });
            this.getRecommendationsGrid().setFilterProperty('inspection', cfg.values.inspection_id, 100);
        }
        return this._recommendationsGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'RECOMENDAÇÕES',
            layout: 'form',
            frame: true,
            height: 535,
            border: false,
            autoScroll: true,
            overflow: 'auto',
            bodyStyle: 'padding: 5px',
            items: [
                this.getRecommendationsGrid(cfg),
            ],
        });

        Ext.apply(cfg, {

        });

        corregedoria.inspection.inspection.filling.recommendations.Launcher.superclass.constructor.call(this, cfg);

    }
});
