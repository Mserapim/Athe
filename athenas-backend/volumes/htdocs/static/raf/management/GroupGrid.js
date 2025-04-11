Ext._define('raf.management.GroupGrid', {
    extend: 'Ext.grid.GridPanel',

    factoryStore: function(cfg) {
        if(!this._groupStore) {
            this._groupStore = Ext._create('Ext.data.GroupingStore', {
                autoLoad: true,
                baseParams: {
                    employee: 0
                },
                proxy: Ext._create('Ext.data.HttpProxy', {
                    url: core.callAction('RAFFunctionalActivityReport', 'all_rafstatus'),
                }),
                groupField: 'year',
                groupDir: 'DESC',
                reader: Ext._create('Ext.data.JsonReader', {
                    totalProperty: 'count',
                    root: 'collection',
                    fields: [
                        {type: "string", name: "month_unicode"},
                        {type: "integer", name: "month"},
                        {type: "integer", name: "year"},
                    ]
                })
            });
        }
        return this._groupStore;
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = new Ext.grid.ColumnModel({
                columns: [
                    {header: 'Ano', dataIndex: 'year', width: 40},
                    {header: 'Mês', dataIndex: 'month_unicode', width: 80},
                ],
            });
        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.apply(
            cfg,
            {
                loadMask: true,
                ds: this.factoryStore(cfg),
                colModel: this.getColumnModel(),
                view: new Ext.grid.GroupingView({
                    startCollapsed: true,
                    forceFit: true,
                    showGroupName: false,
                    enableNoGroups: false,
                    enableGroupingMenu: false,
                    hideGroupedColumn: true
                })
            }
        );
        raf.management.GroupGrid.superclass.constructor.call(this, cfg);
    }
});
