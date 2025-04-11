Ext._define('corregedoria.cirdir.history.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.cirdir.history.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Data', width: 120, sortable: false, dataIndex: 'dt_action', renderer: Ext.util.Format.dateRenderer('d/m/Y H:i:s'), menuDisabled: true, },
                    {header: 'Ação', id: 'autoExpandColumn', sortable: false, dataIndex: 'action', menuDisabled: true, },
                    {header: 'Servidor', width: 450, sortable: false, dataIndex: 'employee_unicode', menuDisabled: true, },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.cirdir.history.Restful',
    'corregedoria.cirdir.history.Grid'
);
