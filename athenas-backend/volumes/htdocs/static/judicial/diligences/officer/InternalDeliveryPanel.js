
Ext._define('judicial.diligences.officer.InternalDeliveryPanel', {
    extend: 'Ext.Panel',

    mixins: {
        '1': 'judicial.diligences.officer.FactoryDiligenceGridMixin',
    },

    getDiligenceGrid: function(cfg) {
        if (!this._diligenceGrid) {
            var self = this;

            this._diligenceGrid = this.factoryDiligenceGrid({
                gridConfig: {
                    region: 'center',
                    minWidth: 500,
                    gridAutoLoad: false,
                    configOrderToolBar: ['search', 'openPrinter', '-', 'openLawsuit', '-', 'response', '->'],
                    columnAction: false,
                    hiddenColumns: [
                        'icon_status', 'responsible_delivering_unicode', 'deadline', 'title'
                    ],
                    viewConfig: {
                        getRowClass: function(record, rowIndex, rp, ds){
                            if(record.data.response_is_signed_by_officer)
                                return 'x-grid3-green-simple';
                            else if(record.data.has_response_officer)
                                return 'x-grid3-yellow-simple';
                        }
                    },
                    doubleClickHandler: function() {
                        this.response()
                    },
                },
                filters: [
                    {
                        property: 'who_type',
                        value: 7,
                        stage: 1000
                    },
                    {
                        property:'date_receipt_diligence__isnull',
                        value: false,
                        stage: 1001
                    }
                ],
                selection: function(record) { self.diligence(record); },
                loadCallback: {
                    scope: this,
                    fn: function(store) {
                        this.setTitle('Internas (' + store.getTotalCount() + ')')
                    }
                }
            })
        }

        return this._diligenceGrid;
    },

    diligence: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._diligence = value;

            if(dispatch)
                this.diligenceObserve();
        }

        return this._diligence;
    },

    diligenceObserve: function() {
        var diligence = this.diligence();
        this.getTilePanel().setPageContent('');
        tile = this.getTilePanel();

        if(diligence) {
            var rest = Ext._create('judicial.diligences.JudicialDiligenceRestful');
            var mask = new Ext.LoadMask(tile.getEl(), {msg: 'carregando documento...'});

            mask.show();
            rest.rendered(
                diligence.get('pk'),
                {
                    scope: this,
                    fn: function(rst) {
                        if(rst.success) {
                            tile.setPageContent(rst.rendered);
                            (rst.extra_pages || []).forEach(
                                function(page) {
                                    tile.addPageContent(page);
                                }
                            );
                        }else {
                            tile.setPageContent('');
                            Ext.Msg.show({
                                title: 'Carregando documento',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    }
                },
                {
                    scope: this,
                    fn: function() {
                        tile.setPageContent('');
                        Ext.Msg.show({
                            title: 'Carregando documento',
                            msg: 'Recurso indisponivel no momento.',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                },
                {
                    fn: function() { mask.hide() }
                }
            )
        }
    },

    getTilePanel: function(cfg) {
        if(!this._tilePanel)
            this._tilePanel = Ext._create('core.TilePagePanel', {
                flex: 1,
                papperModel: (cfg.tilePapperModel || 'a4')
            });

        return this._tilePanel;
    },

    getDocumentPanel: function(cfg) {
        if(!this._deliveryControlPanel)
            this._deliveryControlPanel = Ext._create('Ext.Panel', {
                region: 'east',
                minWidth: 830,
                width: 830,
                split: true,
                layout: {
                    type: 'vbox',
                    align: 'stretch',
                },
                items: [
                    this.getTilePanel(cfg),
                ]
            });

        return this._deliveryControlPanel;
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Internas',
            layout: 'border',
            listeners: {
                activate: function() {
                    this.getDiligenceGrid().getStore().reload();
                }
            },
            items:[
                this.getDiligenceGrid(cfg),
                this.getDocumentPanel(cfg)
            ]
        });

        judicial.diligences.officer.InternalDeliveryPanel.superclass.constructor.call(this, cfg);
    }

})
