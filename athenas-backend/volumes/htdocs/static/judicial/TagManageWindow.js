Ext._define('judicial.TagManageWindow', {
    extend: 'Ext.Window',

    _markerLawsuit: function(pkset) {
        var rest = this.getTagGrid().factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Marcando o procedimento...'});

        mask.show();
        rest.markerLawsuit(
            this.tag(),
            pkset,
            {
                scope: this,
                fn: function() {
                    this.getLawsuitGrid().getStore().reload();
                    this.getLawsuitMarkerGrid().getStore().reload();
                    this.getTagGrid().getStore().reload();
                }
            },
            {
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Marcando o procedimento...',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                fn: function() {
                    mask.hide();
                }
            }
        );

    },

    markerLawsuit: function(selected) {
        selected = (selected || this.getLawsuitGrid().getSelectionModel().getSelections());
        if(selected.length > 0)
            this._markerLawsuit(selected.map(function(data) { return data.get('pk'); }));
        else
            Ext.Msg.show({
                title: 'Marcar Procedimentos',
                msg: 'Primeiro selecione o procedimento que deseja marcar.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    _unmarkerLawsuit: function(pkset) {
        var rest = this.getTagGrid().factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Marcando o procedimento...'});

        mask.show();
        rest.unmarkerLawsuit(
            this.tag(),
            pkset,
            {
                scope: this,
                fn: function() {
                    this.getLawsuitGrid().getStore().reload();
                    this.getLawsuitMarkerGrid().getStore().reload();
                    this.getTagGrid().getStore().reload();
                }
            },
            {
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Marcando o procedimento...',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    unmarkerLawsuit: function(selected) {
        selected = (selected || this.getLawsuitMarkerGrid().getSelectionModel().getSelections());

        if(selected.length > 0)
            this._unmarkerLawsuit(selected.map(function(data) { return data.get('pk'); }));
        else
            Ext.Msg.show({
                title: 'Marcar Procedimentos',
                msg: 'Primeiro selecione o procedimento que deseja desmarcar.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    getControlPanel: function() {
        if(!this._controlPanel)
            this._controlPanel = Ext._create('Ext.Panel', {
                width: 40,
                height: 600,
                boder: false,
                frame: true,
                layout: 'vbox',
                bodyStyle: {
                    'border-top': 0,
                    'border-bottom': 0,
                },
                items: [
                    {
                        xtype: 'panel',
                        flex: 1.0
                    },

                    {
                        xtype: 'button',
                        iconCls: 'icon-core icon-core-add-selected',
                        width: 28,
                        height: 30,
                        style: {
                            padding: '2px 0 0 0',
                        },
                        scope: this,
                        handler: function() { this.markerLawsuit(); }
                    },

                    {
                        xtype: 'button',
                        iconCls: 'icon-core icon-core-remove-selected',
                        width: 28,
                        height: 30,
                        style: {
                            padding: '2px 0 0 0',
                        },
                        scope: this,
                        handler: function() { this.unmarkerLawsuit(); }
                    },
                    {
                        xtype: 'panel',
                        flex: 1.0
                    }
                ]
            });

        return this._controlPanel;
    },

    getLawsuitMarkerGrid: function() {
        if(!this._lawsuitMarkerGrid) {
            var me = this;
            this._lawsuitMarkerGrid = Ext._create('judicial.OutCourtLawsuitGrid', {
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
            this._lawsuitGrid = Ext._create('judicial.OutCourtLawsuitGrid', {
                title: 'Procedimentos',
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

            this._lawsuitGrid.setFilterProperty('location__pk', cfg.params.work_place, 1000);
        }

        return this._lawsuitGrid;
    },

    getTagGrid: function(cfg) {
        if(!this._tagGrid) {
            this._tagGrid = Ext._create('judicial.TagGrid', {
                title: 'Localizadores',
                region: 'west',
                width: 250,
                minWidth: 200,
                split: true,
                gridAutoLoad: false,
                columnAction: false,
                border: false,
                configOrderToolBar: ['add', 'edit', 'remove','-'],
            });

            this._tagGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sm) {
                    var selected = sm.getSelected();
                    if(selected)
                        this.tag(selected.get('pk'));
                    else
                        this.tag(null);
                }
            });
            this._tagGrid.setParam('tag_type', cfg.params.tag_type );
            this._tagGrid.setFilterProperty('tag_type', cfg.params.tag_type, 1000, false);
            this._tagGrid.setParam('work_place', cfg.params.work_place);
            this._tagGrid.setFilterProperty('work_place', cfg.params.work_place, 1001, true);

        }

        return this._tagGrid;
    },

    getMainPanel: function(cfg) {
        if(!this._mainPanel)
            this._mainPanel = Ext._create('Ext.Panel', {
                layout: 'border',
                region: 'center',
                height: 600,
                items : [
                    this.getTagGrid(cfg),
                    {
                        xtype: 'panel',
                        region: 'center',
                        layout: {
                            type:'hbox',
                            align: 'stretch'
                        },
                        minWidth: 700,
                        border: false,
                        items: [
                            this.getLawsuitGrid(cfg),
                            this.getControlPanel(),
                            this.getLawsuitMarkerGrid()
                        ]
                    },
                ]
            });

        return this._mainPanel;
    },

    lawsuit: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._lawsuit = value;

            if(dispatch) this.observer();
        }

        return this._lawsuit;
    },

    tag: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._tag = value;

            if(dispatch) this.observer();
        }

        return this._tag;
    },

    observer: function() {
        var tag = this.tag();
        var lawsuit = this.lawsuit();

        if(lawsuit)
            this.getLawsuitGrid().setFilterProperty('pk__in', lawsuit, 100, false);
        else
            this.getLawsuitGrid().removeFilterProperty('pk__in', 100, false);

        if(tag) {
            this.getControlPanel().enable();

            this.getLawsuitGrid().enable();
            this.getLawsuitGrid().setParam('tags', tag);
            this.getLawsuitGrid().setFilterProperty('tags', tag, -100);

            this.getLawsuitMarkerGrid().enable();
            this.getLawsuitMarkerGrid().setParam('tags', tag);
            this.getLawsuitMarkerGrid().setFilterProperty('tags', tag, 100);

        } else {
            this.getControlPanel().disable();

            this.getLawsuitGrid().disable();
            this.getLawsuitGrid().setParam('tags', 0);
            this.getLawsuitGrid().removeFilterProperty('tags', -100);


            this.getLawsuitMarkerGrid().disable();
            this.getLawsuitMarkerGrid().setParam('tags', 0);
            this.getLawsuitMarkerGrid().removeFilterProperty('tags', 100, false);
            this.getLawsuitMarkerGrid().getStore().removeAll();

        }

    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: false,
                items: [
                    this.getMainPanel(cfg),
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {

        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            title: 'Gerenciar Localizadores',
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
