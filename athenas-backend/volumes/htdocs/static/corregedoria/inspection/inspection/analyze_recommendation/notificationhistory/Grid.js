Ext._define('corregedoria.inspection.inspection.follow_recommendation.notificationhistory.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.inspection.inspection.follow_recommendation.notificationhistory.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    { header: 'Protocolo', dataIndex: 'protocol_codigo', id: 'autoExpandColumn' },
                    { header: 'Enviado em...', dataIndex: 'date', width: 125, },
                    { header: 'Vencimento', dataIndex: 'deadline', width: 125, },
                    { xtype: 'actioncolumn', width: 100, scope: this, align: 'center',
                        items: [
                            {
                                tooltip: 'Visualizar Protocolo',
                                icon: '/' + global.Context + '/static/corregedoria/images/open-bookmark.png',
                                handler: function(grid, row, col) {
                                    grid.getSelectionModel().selectRow(row);
                                    var record = grid.getStore().getAt(row);
                                    console.log(record);
                                    edocs.protocolo.openReletad(record.data.protocol);
                                },
                                scope: this
                            },
                        ]
                    }
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.inspection.inspection.follow_recommendation.notificationhistory.Restful',
    'corregedoria.inspection.inspection.follow_recommendation.notificationhistory.Grid'
);
