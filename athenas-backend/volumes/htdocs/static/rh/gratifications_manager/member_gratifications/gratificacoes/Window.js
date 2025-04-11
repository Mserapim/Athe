Ext._define('rh.gratifications_manager.member_gratifications.gratificacoes.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.gratifications_manager.member_gratifications.gratificacoes.Restful',

    width: 900,
    tabPanelHeight: 500,

    constructor: function(cfg) {
        rh.gratifications_manager.member_gratifications.gratificacoes.Window.superclass.constructor.call(this, cfg);
    },

    getFormPanel: function(cfg_window, cfg) {
        if(!this._formPanel){
            cfg = core.nullValue(cfg, {});
            
            Ext.apply(
                cfg,
                {
                    border: false,
                    height: 500,
                    items: [
                        this.getTabPanel(cfg, cfg_window),
                    ]
                }
            );
            
            this._formPanel = Ext._create('Ext.form.FormPanel', cfg);
        }
        return this._formPanel;
    },

    getTabPanel: function(cfg_window, cfg) {
        if(!this._tabPanel){
            cfg = core.nullValue(cfg, {});
            
            Ext.apply(
                cfg,
                {
                    border: false,
                    activeTab: 0,
                    height: this.tabPanelHeight,
                    items: [
                        this.getPanelInformation(cfg_window),
                    ]
                }
            );
            
            this._tabPanel = Ext._create('Ext.TabPanel', cfg);
        }
        return this._tabPanel;
    },

    getPanelInformation: function(cfg_window, cfg) {
        if(!this._informationPanel){
            cfg = core.nullValue(cfg, {});
            Ext.applyIf(
                cfg,
                {
                    title: 'Dados',
                    frame: true,
                    border: false,
                    layout: 'form',
                    defaults: {
                        width: 400
                    }
                }
            );
            Ext.apply(cfg, {items: [this.getPanelInformationItems(cfg_window)]});
            this._informationPanel = Ext._create('Ext.Panel', cfg);
        }
        return this._informationPanel;
    },

    getPanelInformationItems: function(cfg_window) {
        return [
            {
                xtype: "textfield", 
                fieldLabel: "Servidor", 
                name: "servidor_unicode",
                disabled: true,
                width: 380,
            },

            {
                xtype: "textfield", 
                fieldLabel: "Gratificação", 
                name: "evento_unicode",
                disabled: true,
                width: 380,
            },
            {
                fieldLabel: "Qtd Dias Consolidado",
                name: "qtd_dias_consolidado",
                xtype: "textfield",
                disabled: true,
                width: 150,
            },
            {
                fieldLabel: "Qtd Dias Deferido",
                name: "qtd_dias_deferido",
                xtype: "textfield",
                allowBlank: true,
                width: 150,
            },
        ];
    },

    getPanelDesigs: function(cfg, cfg_window) {
        cfg = core.nullValue(cfg, {});

        if(!this._desigsPanel){
            var designacoesGridPanel = Ext._create(
                'rh.gratifications_manager.cumulative_exercises_permanent.designacoes.Grid',
                {
                    height: 400,
                    gridAutoLoad: true,
                    border: false,
                    exercCumulPermId: cfg.oId,
                }
            );

            Ext.apply(
                cfg,
                {
                    title: 'Designações',
                    frame: true,
                    border: false,
                    items: [designacoesGridPanel],
                }
            );

            this._desigsPanel = Ext._create('Ext.Panel', cfg);
        }
        return this._desigsPanel;
    },
});

