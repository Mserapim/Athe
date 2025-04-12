Ext._define('common.document_access.control.Manage', {
    extend: 'toolkit.widget.TabPanel',

    _gridResizeEvent: function (grid, adjWidth) {
        grid.getKeywordField().setWidth(adjWidth - 290);
    },

    getControlGrid: function (cfg) {
        if (!this._controlGrid) {
            this._controlGrid = Ext._create('common.document_access.control.Grid', {
                region: 'center',
                gridAutoLoad: true,
                allowCreate: false,
                allowUpdate: false,
                allowRemove: false,
                columnAction: false,
                title: 'Classificados'
            });

            this._controlGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function (selectionModel) {
                    var selections = selectionModel.getSelections();

                    if (selections.length > 0) {
                        this.control(selections[0]);
                    } else {
                        this.control(null);
                    }
                }
            });

            this._controlGrid.getStore().on({
                scope: this,
                'load': this.observeControl
            });

            this._controlGrid.on({
                scope: this,
                activate: function() {
                    this._controlGrid.getStore().reload();
                },
                resize: this._gridResizeEvent,
            });
        }

        return this._controlGrid;
    },

    getDeclassifiedControlGrid: function (cfg) {
        if (!this._declassifiedControlGrid) {
            this._declassifiedControlGrid = Ext._create('common.document_access.control.Grid', {
                region: 'center',
                gridAutoLoad: true,
                allowCreate: false,
                allowUpdate: false,
                allowRemove: false,
                columnAction: false,
                title: 'Desclassificados',
                hiddenMenuItems: ['declassify', 'deadlineChange']
            });

            this._declassifiedControlGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function (selectionModel) {
                    var selections = selectionModel.getSelections();

                    if (selections.length > 0) {
                        this.control(selections[0]);
                    } else {
                        this.control(null);
                    }
                }
            });

            this._declassifiedControlGrid.getStore().on({
                scope: this,
                'load': this.observeControl
            });

            this._declassifiedControlGrid.on({
                scope: this,
                activate: function() {
                    this._declassifiedControlGrid.getStore().reload();
                },
                resize: this._gridResizeEvent,
            });
        }

        return this._declassifiedControlGrid;
    },

    control: function (value, observe) {
        observe = (observe === undefined ? true : observe);

        if (value !== undefined) {
            this._control = value;
            if (observe)
                this.observeControl();
        }

        return this._control;
    },

    observeControl: function () {
        var value = this.control();

        if (!value) {
            this.getContentTilePanel().setPageContent('');
            this.getContentTilePanel().disable();
            this.getDetailTilePanel().setPageContent('');
            this.getDetailTilePanel().disable();
            return;
        }

        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Carregando...'});
        mask.show();

        var rest = this.getControlGrid().factoryRestful();
        rest.documentRenderer(
            {pk: value.data.pk},
            {
                scope: this,
                fn: function(obj) {
                    if (!obj.success) {
                        return;
                    }

                    this.getContentTilePanel().enable();
                    this.getContentTilePanel().setPageContent(obj.content);

                    var self = this;
                    obj.extra_pages.forEach(function (page) {
                        self.getContentTilePanel().addPageContent(page);
                    });

                    this.getDetailTilePanel().enable();
                    this.getDetailTilePanel().setPageContent(obj.detail);
                }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: this.title,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: message,
                        minWidth: 250
                    });
                }
            },
            {
                scope: this,
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    getContentTilePanel: function (cfg) {
        if (!this._contentTilePanel) {
            this._contentTilePanel = Ext._create('core.TilePagePanel', {
                title: 'Conteúdo',
            });
        }

        return this._contentTilePanel;
    },

    getDetailTilePanel: function (cfg) {
        if (!this._detailTilePanel) {
            this._detailTilePanel = Ext._create('core.TilePagePanel', {
                title: 'Detalhes',
            });
        }

        return this._detailTilePanel;
    },

    getLeftTabPanel: function (cfg) {
        if (!this._tabLeftPanel) {
            this._tabLeftPanel = Ext._create('Ext.TabPanel', {
                activeTab: 0,
                region: 'west',
                border: false,
                split: true,
                items: [
                    this.getControlGrid(cfg),
                    this.getDeclassifiedControlGrid(cfg),
                ],
            });
        }

        return this._tabLeftPanel;
    },

    getRightTabPanel: function (cfg) {
        if (!this._tabRightPanel) {
            this._tabRightPanel = Ext._create('Ext.TabPanel', {
                activeTab: 0,
                region: 'center',
                items: [
                    this.getContentTilePanel(cfg),
                    this.getDetailTilePanel(cfg),
                ],
            });
        }

        return this._tabRightPanel;
    },

    _resizeEvent: function (panel, adjWidth) {
        toolkit.util.updateGridAndTileDimensions({
            target: this.getLeftTabPanel(),
            containerWidth: adjWidth,
        });
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Gestor de controle de acesso',
        });

        Ext.apply(cfg, {
            layout: 'border',
            items: [
                this.getLeftTabPanel(cfg),
                this.getRightTabPanel(cfg)
            ],
            listeners: {
                scope: this,
                resize: this._resizeEvent,
            },
        });

        this.getControlGrid(cfg).setFilterProperty('control_type__isnull', 'False', 1000);
        this.getDeclassifiedControlGrid(cfg).setFilterProperty('control_type__isnull', 'True', 1000);

        common.document_access.control.Manage.superclass.constructor.call(this, cfg);
    }
});
