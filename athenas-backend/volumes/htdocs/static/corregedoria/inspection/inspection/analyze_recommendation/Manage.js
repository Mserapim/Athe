Ext._define('corregedoria.inspection.inspection.analyze_recommendation.Manage', {
  extend: 'toolkit.widget.TabPanel',

    getGridInspection: function() {
        if(!this._gridInspection) {
            this._gridInspection = Ext._create('corregedoria.inspection.inspection.Grid', {
                region: 'center',
                id: 'gridInspection',
                title: 'Lista de Inspeções/Correições',
                gridAutoLoad: true,
                height: Ext.getBody().getBox().height * 0.4,
                width: Ext.getBody().getBox().width * 0.45,
                configOrderToolBar: ['menuRecommendation', 'applyFilter', '->', 'viewReport','-', 'search'],
                hideColumns: ['employee_unicode'],
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                doubleClickHandler: function() { },
                hideActions: ['edit', 'copy', 'remove'],
            });
            this._gridInspection.getStore().on({
                scope: this,
                load: function(sel) {
                    this._gridInspection.getSelectionModel().clearSelections();
                    this.inspection(null);
                },
            });
            this._gridInspection.getSelectionModel().on({
                scope: this,
                selectionchange: function(sel) {
                    var selection = sel.getSelections();
                    if(selection.length > 0)
                        this.inspection(selection[0]);
                    else
                        this.inspection(null);
                }
            });
            this._gridInspection.getWaitingAnalyze();
        }
        return this._gridInspection;
    },

    inspection: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);
        if(value !== undefined) {
            this._inspection = value;
            if(dispatch)
                this.observeInspection();
        }
        return this._inspection;
    },

    observeInspection: function() {
        var value = this.inspection();
        if(value) {
            this.getGridRecommendations().enable();
            this.getGridRecommendations().setParam('inspection', value.get('pk'));
            this.getGridRecommendations().setFilterProperty('inspection', value.get('pk'), 0);
            this.getNewAttachment().enable();
            this.getNewAttachment().setParam('inspection', value.get('pk'));
            this.getNewAttachment().setFilterProperty('inspection', value.get('pk'), 0);
        } else  {
            this.getGridRecommendations().disable();
            this.getGridRecommendations().setParam('inspection', 0);
            this.getGridRecommendations().setFilterProperty('inspection', value, 0, false);
            this.getGridRecommendations().getStore().removeAll();
            this.getNewAttachment().disable();
            this.getNewAttachment().setParam('inspection', 0);
            this.getNewAttachment().setFilterProperty('inspection', value, 0, false);
            this.getNewAttachment().getStore().removeAll();
        }
    },

    getGridRecommendations: function() {
        if(!this._gridRecommendations) {
            this._gridRecommendations = Ext._create('corregedoria.inspection.inspection.analyze_recommendation.Grid', {
                region: 'center',
                title: 'Lista de Recomendações',
                gridAutoLoad: false,
                height:  Ext.getBody().getBox().height * 0.5,
                width: Ext.getBody().getBox().width * 0.45,
                configOrderToolBar: ['->', '-', 'search'],
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                // doubleClickHandler: function() { },
            });
            this._gridRecommendations.getStore().on({
                scope: this,
                load: function(sel) {
                    this._gridRecommendations.getSelectionModel().clearSelections();
                    this.recommendation(null);
                },
            });
            this._gridRecommendations.getSelectionModel().on({
                scope: this,
                selectionchange: function(sel) {
                    var selection = sel.getSelections();
                    if(selection.length > 0)
                        this.recommendation(selection[0]);
                    else
                        this.recommendation(null);
                }
            });
        }
        return this._gridRecommendations;
    },

    getNewAttachment: function(cfg) {
        if(!this._newAttachment)
            this._newAttachment = Ext._create('corregedoria.inspection.attachment.AttachmentGrid', {
                region: 'center',
                title: 'Anexos',
                split: true,
                width: Ext.getBody().getBox().width * 0.45,
                minWidth: Ext.getBody().getBox().width * 0.2,
                maxWidth: Ext.getBody().getBox().width * 0.8
            });
        return this._newAttachment;
    },

    getBoxPanel: function(cfg) {
        if(!this._boxPanel)
            this._boxPanel = Ext._create('Ext.Panel', {
                region: 'west',
                split: true,
                width: Ext.getBody().getBox().width * 0.55,
                minWidth: Ext.getBody().getBox().width * 0.3,
                maxWidth: Ext.getBody().getBox().width * 0.8,
                border: false,
                layout: 'border',
                items: [
                    {
                        xtype: 'tabpanel',
                        region: 'north',
                        activeTab: 0,
                        items: [
                            this.getGridInspection(),
                        ]
                    },
                    {
                        xtype: 'tabpanel',
                        region: 'center',
                        activeTab: 0,
                        items: [
                            this.getGridRecommendations(),
                            this.getNewAttachment(),
                        ]
                    }
                ]
            });
        return this._boxPanel;
    },

    getTilePanel: function(cfg) {
        if(!this._tilePanel)
            this._tilePanel = Ext._create('core.TilePagePanel', {
                region: 'center',
                split: true,
                width: Ext.getBody().getBox().width * 0.45,
                minWidth: Ext.getBody().getBox().width * 0.2,
                maxWidth: Ext.getBody().getBox().width * 0.8
            });
        return this._tilePanel;
    },

    recommendation: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);
        if(value !== undefined) {
            this._recommendation = value;
            if(dispatch)
                this.observeRecommentadion();
        }
        return this._recommendation;
    },

    observeRecommentadion: function() {
        value = this.recommendation();
        if(value) {
            this.getTilePanel().enable();
            this.readView(value.get('pk'));
        }
        else {
            this.getTilePanel().disable();
            this.getTilePanel().setPageContent('');
        }
    },

    readView: function(recommendation) {
        var mask = new Ext.LoadMask(this.getTilePanel().getEl(), {msg: 'Carregado informações...'});
        var rest = this.getGridRecommendations().factoryRestful();
        mask.show();
        this.getTilePanel().enable();
        this.getTilePanel().setPageContent('');
        Ext.Ajax.request({
            url: core.callAction(rest.resource, 'renderer_document'),
            scope: this,
            autoAbort: true,
            params: {
                recommendation: recommendation
            },
            callback: function() {
                mask.hide();
            },
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);
                var me = this;
                if(rst.success) {
                    this.getTilePanel().setPageContent(rst.content);
                }
                else
                    Ext.Msg.show({
                        title: 'Carregando informações',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function() {
                Ext.Msg.show({
                    title: 'Carregando informações',
                    msg: 'Recurso indisponivel no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};
        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Recomendações'
            }
        );
        Ext.apply(
            cfg,
            {
                layout: 'border',
                border: false,
                items: [
                    this.getBoxPanel(cfg),
                    this.getTilePanel(cfg)
                ],
            }
        );
        corregedoria.inspection.inspection.analyze_recommendation.Manage.superclass.constructor.call(this, cfg);
        this.inspection(cfg.oId === undefined ? null : cfg.oId);
        this.recommendation(cfg.oId === undefined ? null : cfg.oId);
    },
});
