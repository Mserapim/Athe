
Ext._define('judicial.diligences.officer.CancelDeliveryPanel', {
    extend: 'Ext.Panel',

    mixins: {
        '1': 'judicial.diligences.officer.FactoryDiligenceGridMixin',
        '2': 'judicial.diligences.DeliveryAttemptPanel',
    },

    getDiligenceGrid: function(cfg) {
        if (!this._diligenceGrid) {
            var self = this;

            this._diligenceGrid = this.factoryDiligenceGrid({
                gridConfig: {
                    region: 'center',
                    minWidth: 500,
                    gridAutoLoad: false,
                    configOrderToolBar: ['search', 'openPrinter', '-', 'openLawsuit', '->'],
                    columnAction: false,
                    hiddenColumns: [
                        'icon_status', 'responsible_delivering_unicode', 'deadline', 'title'
                    ]
                },
                filters: [
                    {
                        property: 'delivery_status',
                        value: 8,
                        stage: 1000
                    }
                ],
                selection: function(record) {
                    if(record)
                        self.diligence(record.get('pk'));
                 },
                loadCallback: {
                    scope: this,
                    fn: function(store) {
                        this.setTitle('Devolvidas (' + store.getTotalCount() + ')')
                    }
                }
            })
        }

        return this._diligenceGrid;
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Devolvidas',
            listeners: {
                activate: function() {
                    this.getDiligenceGrid().getStore().reload();
                }
            }
        });

        this.configurePanel(cfg);
        judicial.diligences.officer.CancelDeliveryPanel.superclass.constructor.call(this, cfg);
    }

})
