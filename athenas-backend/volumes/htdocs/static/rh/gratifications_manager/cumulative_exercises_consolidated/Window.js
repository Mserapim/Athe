 Ext._define('rh.gratifications_manager.cumulative_exercises_consolidated.Window', {
    extend: 'Ext.Window',

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Exercícios Cumulativos',
                closable: true,
                resizable: false,
                border: false,
                width: 1200,
                height: 650,
                items: [
                    new rh.gratifications_manager.cumulative_exercises_consolidated.SubstitutionsTabPanel({}, cfg.oId),
                ],
            }
        );

        rh.gratifications_manager.cumulative_exercises_consolidated.Window.superclass.constructor.call(this, cfg);
    },
});

Ext._define('rh.gratifications_manager.cumulative_exercises_consolidated.SubstitutionsTabPanel', {
    extend: 'Ext.Panel',

    constructor: function (cfg, consolidatedId) {
        cfg = core.nullValue(cfg, {});

        var substitutionGridPanel = Ext._create(
            'rh.gratifications_manager.cumulative_exercises_consolidated.substitutions.Grid',
            {
                height: 600,
                gridAutoLoad: true,
                border: false,
                consolidatedId: consolidatedId,
            }
        );

        Ext.applyIf(
            cfg,
            {
                title: 'Substituições',
                items: [substitutionGridPanel],
            }
        );
    
        rh.gratifications_manager.cumulative_exercises_consolidated.SubstitutionsTabPanel.superclass.constructor.call(this, cfg);
    }
});