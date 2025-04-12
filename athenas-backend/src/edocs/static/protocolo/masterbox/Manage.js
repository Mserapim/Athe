Ext._define('edocs.protocolo.masterbox.Manage', {
    extend: 'toolkit.widget.TabPanel',

    _gridSelectionChangeEvent: function (selectionModel) {
        var selections = selectionModel.getSelections();

        if (selections.length > 0) {
            this.protocol(selections[0].get('pk'));
            return;
        }

        this.protocol(null);
    },

    getProtocolGrid: function (cfg) {
        if (!this._protocolGrid) {
            this._protocolGrid = Ext._create('edocs.protocolo.masterbox.Grid', {
                region: 'west',
                border: false,
                split: true,
                gridAutoLoad: true,
                columnAction: false,
                configOrderToolBar: ['menu', '-', 'search', '->', 'download'],
                hideItemsToolbar: ['download'],
                keywordFieldWidth: 600,
                doubleClickHandler: function() {
                    return null;
                },
            });

            this._protocolGrid.on({
                scope: this,
                resize: function (grid, adjWidth) {
                    this._protocolGrid.getKeywordField().setWidth(adjWidth - 150);
                },
            });

            this._protocolGrid.getSelectionModel().on({
                scope: this,
                selectionchange: this._gridSelectionChangeEvent,
            });

            this._protocolGrid.setSortProperty('codigo', 'DESC', 100);
        }

        return this._protocolGrid;
    },

    getProtocolViewer: function (cfg) {
        if (!this._datailProtocolTilePanel) {
            this._datailProtocolTilePanel = Ext._create('core.TilePagePanel', {
                disabled: true,
                region: 'center',
            });
        }

        return this._datailProtocolTilePanel;
    },

    protocol: function (value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if (value !== undefined) {
            this._protocol = value;

            if (dispatch) {
                this.observerProtocol();
            }
        }

        return this._protocol;
    },

    observerProtocol: function () {
        var value = this.protocol();

        if (!value) {
            this.getProtocolViewer().disable();
            this.getProtocolViewer().setPageContent('');
            return;
        }

        var mask = new Ext.LoadMask(
            this.getProtocolViewer().getEl(),
            {msg: 'Buscando informações...'}
        );
        mask.show();

        this.getProtocolGrid().factoryRestful().rendererDocument(
            value,
            {
                scope: this,
                fn: function (document) {
                    this.getProtocolViewer().enable();
                    this.getProtocolViewer().setPageContent(document.content);
                    this.getProtocolViewer().setPageContent(document.appends);
                }
            },
            {
                fn: function (message) {
                    Ext.Msg.show({
                        title: 'Buscando informações',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                fn: function () {
                    mask.hide();
                }
            },
        );
    },

    _resizeEvent: function (panel, adjWidth) {
        toolkit.util.updateGridAndTileDimensions({
            target: this.getProtocolGrid(),
            containerWidth: adjWidth,
        });
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Caixa mestre de protocolos',
        });

        Ext.apply(cfg, {
            layout: 'border',
            items: [
                this.getProtocolGrid(cfg),
                this.getProtocolViewer(cfg),
            ],
            listeners: {
                scope: this,
                resize: this._resizeEvent,
            },
        });

        edocs
          .protocolo
          .masterbox
          .Manage
          .superclass
          .constructor
          .call(this, cfg);

        this.observerProtocol();
    }
});
