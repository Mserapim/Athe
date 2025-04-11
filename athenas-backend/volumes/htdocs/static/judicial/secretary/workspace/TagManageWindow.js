Ext._define('judicial.secretary.workspace.TagManageWindow', {
    extend: 'judicial.TagManageWindow',

    getLawsuitMarkerGrid: function() {
        if(!this._lawsuitMarkerGrid) {
            var me = this;
            this._lawsuitMarkerGrid = Ext._create('judicial.secretary.workspace.Grid', {
                title: 'Procedimentos Marcados',
                toolbarHideLabel: true,
                flex: 1.0,
                minWidth: 345,
                doubleClickHandler: function() {
                    me.unmarkerLawsuit();
                },
                border: false,
                frame: false,
                gridAutoLoad: false,
                configOrderToolBar: ['search'],
                columnAction: false,
                hideColumns: ['deadline','type_lawsuit_display','current_location_unicode','last_document_signed','location_unicode','year','number_lawsuit']
            });
        }

        return this._lawsuitMarkerGrid;
    },

    getLawsuitGrid: function(cfg) {
        if(!this._lawsuitGrid) {
            var me = this;
            this._lawsuitGrid = Ext._create('judicial.secretary.workspace.Grid', {
                title: 'Procedimentos na secretaria',
                toolbarHideLabel: true,
                flex: 1.0,
                minWidth: 345,
                doubleClickHandler: function() {
                    me.markerLawsuit();
                },
                border: false,
                frame: false,
                gridAutoLoad: false,
                configOrderToolBar: ['search',],
                columnAction: false,
                hideColumns: ['deadline','type_lawsuit_display','current_location_unicode','last_document_signed','location_unicode','year','number_lawsuit']
            });

        }

        return this._lawsuitGrid;
    },

    constructor: function(cfg) {

        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            title: 'Gerenciar Localizadores de Secretaria',
            border: false,
            width: 951
        });

        Ext.apply(cfg, {
            items: [
                this.getFormPanel(cfg)
            ],
            buttons: [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() {
                        core.invokeCallback((this.callback || {}).success);
                        this.close();
                    }
                }
            ]
        });

        this.lawsuit(cfg.params.lawsuit, false);


        judicial.TagManageWindow.superclass.constructor.call(this, cfg);

        this.on({
            afterrender: function(me) {
                me.observer();
            }
        });
    }
});
