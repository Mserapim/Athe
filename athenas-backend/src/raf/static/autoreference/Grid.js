Ext._define('raf.autoreference.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'raf.autoreference.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'unicode', id: 'autoExpandColumn', hidden: true},
                    {header: 'Ajuste?', dataIndex: 'is_adjustment', width: 50, renderer: toolkit.util.formatIconYesNo, },
                    {header: 'Removido?', dataIndex: 'removed', width: 70, renderer: toolkit.util.formatIconYesNo, },
                    {header: 'Fonte', dataIndex: 'source_add_display', width: 60},
                    {header: 'Processo', dataIndex: 'process_number', width: 230},
                    {header: 'Data', dataIndex: 'date', width: 110, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')},
                    {header: '', xtype: 'actioncolumn', width: 50, scope: this, menuDisabled: true,
                        items: [
                            {
                                tooltip: 'Mais informações...',
                                icon: '/'+ global.Context + '/static/images/icons/document-arrow.png',
                                scope:this,
                                handler: function(grid, row, col) {
                                    grid.getSelectionModel().selectRow(row);
                                    var record = grid.getStore().getAt(row);

                                    if (record.data.source_add == 1)
                                        if (record.data.is_adjustment == false)
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

                                    if (record.data.source_add == 2)
                                        if (record.data.is_adjustment == false)
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

                                    if (record.data.source_add == 3)
                                        if (record.data.is_adjustment == false)
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
                                        
                                    if (record.data.source_add == 4)
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
    'raf.autoreference.Restful',
    'raf.autoreference.Grid'
);
