Ext._define('edocs.protocolo.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getMainBoxTilePanel: function(cfg) {
        if (!this._mainBoxTilePanel) {
            this._mainBoxTilePanel = Ext._create('core.TilePagePanel', {
                region: 'center',
            });
        }

        return this._mainBoxTilePanel;
    },

    getPersonBoxTilePanel: function(cfg) {
        if (!this._personBoxTilePanel) {
            this._personBoxTilePanel = Ext._create('core.TilePagePanel', {
                region: 'center',
            });
        }

        return this._personBoxTilePanel;
    },

    getHistoryBoxTilePanel: function(cfg) {
        if (!this._historyBoxTilePanel) {
            this._historyBoxTilePanel = Ext._create('core.TilePagePanel', {
                region: 'center',
            });
        }

        return this._historyBoxTilePanel;
    },

    getClosedBoxTilePanel: function(cfg) {
        if (!this._closedBoxTilePanel) {
            this._closedBoxTilePanel = Ext._create('core.TilePagePanel', {
                region: 'center',
            });
        }

        return this._closedBoxTilePanel;
    },

    getAspectInboxBoxFn: function(aspectType) {
        var me = this;

        var aspectMap = {
            'general': function() {
                return me.getMainBoxGrid();
            },
            'personal': function() {
                return me.getPersonBoxGrid();
            }
        };

        return aspectMap[aspectType];
    },

    getMainBoxGrid: function(cfg) {
        if (!this._mainBoxGrid) {
            this._mainBoxGrid = Ext._create('edocs.protocolo.box.MainGrid', {
                closedBox: this.getClosedBoxGrid(cfg),
                historyBox: this.getHistoryBoxGrid(cfg),
                otherInboxFn: this.getAspectInboxBoxFn('person'),
                detailView: this.getMainBoxTilePanel(cfg),
                generalProtocol: (cfg || this).generalProtocol,
                split: true,
                region: 'west',
            });

            this._mainBoxGrid.getStore().on({
                scope: this,
                load: function(store, records, options) {
                    this.getMainBoxPanel().setTitle(this._mainBoxGrid.customTitle);
                },
            });
        }
        return this._mainBoxGrid;
    },

    getPersonBoxGrid: function(cfg) {
        if (!this._personBoxGrid) {
            this._personBoxGrid = Ext._create('edocs.protocolo.box.PersonGrid', {
                //keywordFieldWidth: this.calculateBoxPanelWidth() - 330,
                closedBox: this.getClosedBoxGrid(cfg),
                historyBox: this.getHistoryBoxGrid(cfg),
                otherInboxFn: this.getAspectInboxBoxFn('general'),
                detailView: this.getPersonBoxTilePanel(cfg),
                generalProtocol: (cfg || this).generalProtocol,
                split: true,
                region: 'west',
                //width: this.calculateBoxPanelWidth(),
            });

            this._personBoxGrid.getStore().on({
                scope: this,
                load: function(store, records, options) {
                    this.getPersonBoxPanel().setTitle(this._personBoxGrid.customTitle);
                },
            });
        }
        return this._personBoxGrid;
    },

    getHistoryBoxGrid: function(cfg) {
        if (!this._historyBoxGrid) {
            this._historyBoxGrid = Ext._create('edocs.protocolo.box.HistoryGrid', {
                detailView: this.getHistoryBoxTilePanel(),
                mainBox: this.getAspectInboxBoxFn('general'),
                personBox: this.getAspectInboxBoxFn('personal'),
                //keywordFieldWidth: this.calculateBoxPanelWidth() - 330,
                generalProtocol: (cfg || this).generalProtocol,
                split: true,
                region: 'west',
                //width: this.calculateBoxPanelWidth(),
            });

            // this._historyBoxGrid.getStore().on({
            //     scope: this,
            //     load: function(store, records, options) {
            //         this.getHistoryBoxPanel().setTitle(this._historyBoxGrid.customTitle);
            //     },
            // });
        }
        return this._historyBoxGrid;
    },

    getClosedBoxGrid: function(cfg) {
        if (!this._closedBoxGrid) {
            this._closedBoxGrid = Ext._create('edocs.protocolo.box.ClosedGrid', {
                detailView: this.getClosedBoxTilePanel(),
                mainBox: this.getAspectInboxBoxFn('general'),
                personBox: this.getAspectInboxBoxFn('personal'),
                //keywordFieldWidth: this.calculateBoxPanelWidth() - 330,
                split: true,
                region: 'west',
                //width: this.calculateBoxPanelWidth(),
            });
        }
        return this._closedBoxGrid;
    },

    // getSharedBoxPanel: function(cfg) {
    //     if(!this._sharedBoxPanel)
    //         this._sharedBoxPanel = Ext._create('edocs.protocolo.box.SharedGrid', {
    //             title: 'Compartilhado',
    //             keywordFieldWidth: this.calculateBoxPanelWidth() - 95,
    //         });

    //     return this._sharedBoxPanel;
    // },

    // calculateBoxPanelWidth: function() {
    //     var width = (Ext.getBody().getBox().width - 900);
    //     return (width > 525 ? width : 525);
    // },

    getMainBoxPanel: function(cfg) {
        if (!this._mainBoxPanel) {
            this._mainBoxPanel = Ext._create('Ext.Panel', {
                title: 'Principal',
                layout: 'border',
                items: [
                    this.getMainBoxGrid(cfg),
                    this.getMainBoxTilePanel(cfg)
                ],
            });
        }
        return this._mainBoxPanel;
    },

    getPersonBoxPanel: function(cfg) {
        if (!this._personBoxPanel) {
            this._personBoxPanel = Ext._create('Ext.Panel', {
                title: 'Pessoal',
                layout: 'border',
                items: [
                    this.getPersonBoxGrid(cfg),
                    this.getPersonBoxTilePanel(cfg)
                ]
            });
        }
        return this._personBoxPanel;
    },

    getHistoryBoxPanel: function(cfg) {
        if (!this._historyBoxPanel) {
            this._historyBoxPanel = Ext._create('Ext.Panel', {
                title: 'Histórico',
                layout: 'border',
                items: [
                    this.getHistoryBoxGrid(cfg),
                    this.getHistoryBoxTilePanel(cfg)
                ],
                listeners: {
                    scope: this,
                    activate: function() {
                         this.getHistoryBoxGrid(cfg).getStore().reload();
                    }
                }
            });
        }
        return this._historyBoxPanel;
    },

    getClosedBoxPanel: function(cfg) {
        if (!this._closedBoxPanel) {
            this._closedBoxPanel = Ext._create('Ext.Panel', {
                title: 'Finalizado',
                layout: 'border',
                items: [
                    this.getClosedBoxGrid(cfg),
                    this.getClosedBoxTilePanel(cfg)
                ],
                listeners: {
                    scope: this,
                    activate: function() {
                         this.getClosedBoxGrid().getStore().reload();
                    }
                }
            });
        }
        return this._closedBoxPanel;
    },

    _tabPanelRenderEvent: function (tbPanel) {
        var RemoteObserver = core.RemoteObserver;

        var cb = RemoteObserver.on('edoc-load-boxes', {
            scope: this,
            fn: function(result) {
                this.getMainBoxGrid().getStore().reload();
                this.getPersonBoxGrid().getStore().reload();
                // this.getHistoryBoxGrid().getStore().reload();
                // this.getClosedBoxGrid().getStore().reload();
            }
        });
    },

    _tabPanelResizeEvent: function (tbPanel, adjWidth, adjHeight, rawWidth, rawHeight) {
        var newWidth = 0;

        var TABPANEL_WIDTH = adjWidth;
        var TILE_WIDTH = 850;
        var LAPTOP_BASIC_WIDTH = 1366;

        if (TABPANEL_WIDTH <= LAPTOP_BASIC_WIDTH) {
            newWidth = TABPANEL_WIDTH * 45 / 100;  // Use 45% of the TabPanel width
        } else {
            newWidth = TABPANEL_WIDTH - TILE_WIDTH;
        }

        this.getMainBoxGrid().setWidth(newWidth);
        this.getPersonBoxGrid().setWidth(newWidth);
        this.getHistoryBoxGrid().setWidth(newWidth);
        this.getClosedBoxGrid().setWidth(newWidth);
    },

    getBoxPanel: function(cfg) {
        if (!this._boxPanel) {
            this._boxPanel = Ext._create('Ext.TabPanel', {
                region: 'center',
                activeTab: 0,
                border: false,
                items: [
                    this.getMainBoxPanel(cfg),
                    this.getPersonBoxPanel(cfg),
                    this.getHistoryBoxPanel(cfg),
                    this.getClosedBoxPanel(cfg),
                ],
                listeners: {
                    scope: this,
                    render: this._tabPanelRenderEvent,
                    resize: this._tabPanelResizeEvent,
                }
            });
        }

        return this._boxPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                generalProtocol: false,
                title: 'Documentos Eletrônicos'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getBoxPanel(cfg)
                ]
            }
        );

        edocs.protocolo.Manage.superclass.constructor.call(this, cfg);
    }
});
