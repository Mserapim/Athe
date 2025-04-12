Ext._define('raf.searchprocessnumber.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'raf.searchprocessnumber.Window',
    pageSize: 10,

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'unicode', id: 'autoExpandColumn', hidden: true},
                    {header: 'Processo', dataIndex: 'data_processo', width: 450},
                    {header: 'RAF', dataIndex: 'data_raf', width: 500},
                    {header: '', xtype: 'actioncolumn', width: 50, scope: this, menuDisabled: true,
                        items: [
                            {
                                tooltip: 'Mais informações...',
                                icon: '/'+ global.Context + '/static/images/icons/document-arrow.png',
                                scope:this,
                                handler: function(grid, row, col) {
                                    grid.getSelectionModel().selectRow(row);
                                    var record = grid.getStore().getAt(row);
                                    if (record.data.autoreference_source_add == 1)
                                        if (record.data.autoreference_is_adjustment == false)
                                            Ext._create('raf.autoreference.DataEprocWindow', {
                                                params: {
                                                    autoreference: record.data.autoreference_id,
                                                }
                                            }).show();
                                        else {
                                            Ext._create('raf.autoreference.DataAdjustmentWindow', {
                                                params: {
                                                    autoreference: record.data.autoreference_id,
                                                }
                                            }).show();
                                        }
                                    if (record.data.autoreference_source_add == 2)
                                        if (record.data.autoreference_is_adjustment == false)
                                            Ext._create('raf.autoreference.DataEExtWindow', {
                                                params: {
                                                    autoreference: record.data.autoreference_id,
                                                }
                                            }).show();
                                        else {
                                            Ext._create('raf.autoreference.DataAdjustmentWindow', {
                                                params: {
                                                    autoreference: record.data.autoreference_id,
                                                }
                                            }).show();
                                        }
                                    if (record.data.autoreference_source_add == 3)
                                        if (record.data.autoreference_is_adjustment == false)
                                            Ext._create('raf.autoreference.AttendanceWindow', {
                                                params: {
                                                    autoreference: record.data.autoreference_id,
                                                }
                                            }).show();
                                        else {
                                            Ext._create('raf.autoreference.DataAdjustmentWindow', {
                                                params: {
                                                    autoreference: record.data.autoreference_id,
                                                }
                                            }).show();
                                        }
                                    if (record.data.autoreference_source_add == 4)
                                        Ext._create('raf.autoreference.DataAdjustmentWindow', {
                                            params: {
                                                autoreference: record.data.autoreference_id,
                                            }
                                        }).show();
                                }
                            },
                        ]
                    },
                ]
            );
        return this._columnModel;
    }

});

core.RestfulGrid.register(
    'raf.searchprocessnumber.Restful',
    'raf.searchprocessnumber.Grid'
);
