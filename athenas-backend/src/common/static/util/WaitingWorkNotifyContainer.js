// _TODEL_ Em razão do novo Dashboard, excluir botão de "Trabalhos pendentes"
Ext._define('common.util.WaitingWorkNotifyContainer', {
    extend: 'engine.notify.NotifyContainer',
    _title: 'Trabalhos Pendentes',

    actionIconCls: 'icon-rh icon-core-documents',

    bodyHeight: 300,

    getWaitingWorkGrid: function(cfg) {
        if(!this._waitingWorkGrid)
            this._waitingWorkGrid = Ext._create('Ext.grid.GridPanel', {
                height: 300,
                width: 398,
                loadMask: true,
                frame: true,
                store: this.__getStore(),
                autoExpandColumn: 'autoExpandColumn',
                columns:[
                    {header: 'Trabalhos', dataIndex: 'title', id: 'autoExpandColumn'},
                    {header: 'Total', dataIndex: 'count', width: 100 , renderer: this.rendererCount},
                ],
                bbar: new Ext.PagingToolbar({
                    store: this.__getStore(),
                    autoScroll: true,
                    displayInfo: true
                }),
                listeners: {
                    scope: this,
                    dblclick: this.doubleClickEvent
                }
        });

        return this._waitingWorkGrid;
    },

    doubleClickEvent: function(e) {
        var selected = this.getWaitingWorkGrid().getSelectionModel().getSelected();

        if(selected && selected.get('controller'))
            toolkit.Application.createFormFor(selected.get('controller'))

    },

    rendererCount: function(value, cell, record) {
        return '<div style="text-align:right">' + value + ' ' + record.get('type') + '</div>';
    },

    __getStore: function() {
        if(!this._store)
            this._store = new Ext.data.Store({
                proxy: new Ext.data.HttpProxy({
                    url: toolkit.util.Normalize.controller_action('UtilWaitingWorkController', 'store'),
                    method: 'GET',
                    disableCaching: false
                }),
                reader: new Ext.data.JsonReader({
                    root: 'collection',
                    totalProperty: 'count',
                    fields: [
                        {name: 'keyId', type: 'string'},
                        {name: 'title', type: 'string'},
                        {name: 'type', type: 'string'},
                        {name: 'count', type: 'int'},
                        {name: 'controller', type: 'string'},
                    ]
                })
            });

        return this._store;
    },

    handler: function() {
        if(this.collapsed)
            this.getWaitingWorkGrid().getStore().load();
        this.collapseBody();
    },

    getBodyContainer: function(cfg) {
        if(!this._bodyContainer) {
            this._bodyContainer = common.util.WaitingWorkNotifyContainer.superclass.getBodyContainer.call(this, cfg);

            this._bodyContainer.add(
                this.getWaitingWorkGrid(cfg)
            );
        }

        return this._bodyContainer;
    },
});

// _TODEL_ Em razão do novo Dashboard, excluir botão de "Trabalhos pendentes"
//engine.notify.Manage.register('waiting_work', 'common.util.WaitingWorkNotifyContainer');
