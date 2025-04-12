
Ext._define('rh.seriousdiseases.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.seriousdiseases.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Nome', dataIndex: 'name', id: 'autoExpandColumn', width: 90, sortable: true},
                    {header: 'Criado por', dataIndex: 'created_by_unicode', width: 120, sortable: true, hidden: true},
                    {header: 'Criado em', dataIndex: 'created_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), sortable: true, hidden: true},
                    {header: 'Modificado por', dataIndex: 'modified_by_unicode', width: 120, sortable: true, hidden: true},
                    {header: 'Modificado em', dataIndex: 'modified_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), sortable: true, hidden: true}
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'rh.seriousdiseases.Restful',
    'rh.seriousdiseases.Grid'
);

