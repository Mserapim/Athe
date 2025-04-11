Ext._define('corregedoria.inspection.inspection.filling.attachments.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.inspection.inspection.filling.attachments.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    { header: 'Área', dataIndex: 'area_display', width: 150, },
                    { header: 'Tipo', dataIndex: 'attachment_type_display', width: 200, },
                    { header: 'Descrição', dataIndex: 'description', width: 350, },
                    { header: 'Arquivo', dataIndex: 'attached_file_unicode', width: 370, },
                    { xtype: 'actioncolumn', id: 'autoExpandColumn', scope: this,
                        items: [
                            {
                                tooltip: 'Download',
                                icon: '/' + global.Context + '/static/images/attachment.png',
                                handler:function(grid, row, col)
                                {
                                    var record = grid.getStore().getAt(row);
                                    open(record.get('attached_file_url'), '_parent');
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
    'corregedoria.inspection.inspection.filling.attachments.Restful',
    'corregedoria.inspection.inspection.filling.attachments.Grid'
);
