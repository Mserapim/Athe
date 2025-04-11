Ext._define('rh.gratifications_manager.member_gratifications.membros_consolidados.Window', {
    extend: 'Ext.Window',

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Designações de Membro',
                closable: true,
                resizable: false,
                border: false,
                height: 630,
                items: [
                    new rh.gratifications_manager.member_gratifications.membros_consolidados.DesignacoesTabPanel({}, cfg.oId),
                ],
            }
        );

        rh.gratifications_manager.member_gratifications.membros_consolidados.Window.superclass.constructor.call(this, cfg);
    },
});

Ext._define('rh.gratifications_manager.member_gratifications.membros_consolidados.DesignacoesTabPanel', {
    extend: 'Ext.Panel',

    constructor: function (cfg, gratMembroId) {
        cfg = core.nullValue(cfg, {});

        var designacoesGridPanel = Ext._create(
            'rh.gratifications_manager.member_gratifications.designacoes.Grid',
            {
                height: 600,
                gridAutoLoad: true,
                border: false,
                gratMembroId: gratMembroId,
            }
        );

        Ext.applyIf(
            cfg,
            {
                items: [designacoesGridPanel],
            }
        );
    
        rh.gratifications_manager.member_gratifications.membros_consolidados.DesignacoesTabPanel.superclass.constructor.call(this, cfg);

    }
});