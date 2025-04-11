Ext._define('corregedoria.prontuary.individualperformance.coursesparticipation.attachments.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.prontuary.individualperformance.coursesparticipation.attachments.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    { header: 'Descrição', dataIndex: 'description', width: 450, },
                    // { header: 'Arquivo', dataIndex: 'attached_file_unicode', width: 300, },
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
    'corregedoria.prontuary.individualperformance.coursesparticipation.attachments.Restful',
    'corregedoria.prontuary.individualperformance.coursesparticipation.attachments.Grid'
);
