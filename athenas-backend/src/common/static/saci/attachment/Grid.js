Ext._define('common.saci.attachment.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'common.saci.attachment.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    // {
                    //     header: '',
                    //     dataIndex: 'icons',
                    //     width: 50,
                    //     menuDisabled: true,
                    //     renderer: core.rendererIconGrid
                    // },
                    {header: 'Título', dataIndex: 'title', id: 'autoExpandColumn'},
                    {header: 'Anexado por', dataIndex: 'created_by_unicode', width: 150},
                    {header: 'Data', dataIndex: 'created_at', width: 120, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')}
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'common.saci.attachment.Restful',
    'common.saci.attachment.Grid'
);
