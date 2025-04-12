// _TODEL_ Código obsoleto. Customização transferida para river-panel.css
Ext._define('core.dashboard.CustomPanel', {
    extend: 'Ext.Panel',

    _title: 'My title',

    getTitleBarPanel: function (cfg) {
        if (this._titleBarPanel) {
            return this._titleBarPanel;
        }

        this._titleBarPanel = Ext._create('Ext.Panel', {
            region: 'north',
            border: false,
            bodyStyle: [
                'color: #eee;',
                'background-color: #005a7c;',
                'border: 1px solid #eee;',
                'border-bottom: none;',
                'font-size: 14px;',
                'padding: 7px 7px;',
                'font-weight: bold;',
                'cursor: default;',
                'user-select: none;',
            ].join(''),
            html: this._title,
        });

        return this._titleBarPanel;
    },

    setTitle: function (newTitle) {
        // Sobrescreve o valor da config html (os estilos
        // especificados em bodyStyle são preservados)
        Ext.DomHelper.overwrite(this.getTitleBarPanel().body, newTitle);
    },

    getContentPanel: function (cfg) {
        if (this._contentPanel) {
            return this._contentPanel;
        }

        Ext.apply(cfg.contentPanelConfig, {
            region: 'center',
        });

        this._contentPanel = Ext._create('Ext.Panel', cfg.contentPanelConfig);

        return this._contentPanel;
    },

    _configureTitle: function (cfg) {
        if (cfg.hasOwnProperty('title')) {
            if (typeof cfg.title === 'string' && cfg.title.length > 0) {
                this._title = cfg.title;
            }
            delete cfg.title;
        }
    },

    constructor: function (cfg) {
        cfg = cfg || {};
        cfg.contentPanelConfig = cfg.contentPanelConfig || {};

        this._configureTitle(cfg);

        Ext.applyIf(cfg.contentPanelConfig, {
            autoScroll: true,
            bodyStyle: [
                'background-color: white;',
                'border: 1px solid #eee;',
            ].join(''),
            //layout: 'form',
            //padding: 7,
            //items: []
        });

        Ext.apply(cfg, {
            border: false,
            layout: 'border',
            items: [
                this.getTitleBarPanel(cfg),
                this.getContentPanel(cfg),
            ],
        });

        core.dashboard.CustomPanel.superclass.constructor.call(this, cfg);
    },
});
