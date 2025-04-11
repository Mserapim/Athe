Ext._define('adm.contabilidade.budgetaryindicator.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'adm.contabilidade.budgetaryindicator.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Ano', dataIndex: 'year', width: 90},
                    {header: 'I.O.', dataIndex: 'name', width: 120},
                    {header: 'Objeto', dataIndex: 'object_name', id: 'autoExpandColumn'},
                    {header: 'Ação', dataIndex: 'action_unicode', width: 120, hidden: true},
                    {header: 'Fonte', dataIndex: 'source_unicode', width: 238}
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'adm.contabilidade.budgetaryindicator.Restful',
    'adm.contabilidade.budgetaryindicator.Grid'
);
