Ext._define('corregedoria.cirdir.irpf.Grid', {
    extend: 'core.RestfulGrid',

    rest: 'corregedoria.cirdir.irpf.Restful',
    restWindow: 'corregedoria.cirdir.irpf.Window',

    configOrderToolBar: ['add', 'edit', 'remove', 'history', ],

    getHistoryAction: function(cfg) {
        if(!this._historyAction){
            this._historyAction = new Ext.Button({
                xtype: 'button',
                text: ' Histórico',
                iconCls: 'icon-crgmpe icon-crgmpe-list',
                handler: function() {
                    Ext._create('corregedoria.cirdir.HistoryWindow', {
                        params: {
                          controlinformation: cfg.params.controlinformation,
                          criteria_key: 6,
                        },
                    }).show();
                }
            });
        }
        return this._historyAction;
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'title', id: 'autoExpandColumn', },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.cirdir.irpf.Restful',
    'corregedoria.cirdir.irpf.Grid'
);
