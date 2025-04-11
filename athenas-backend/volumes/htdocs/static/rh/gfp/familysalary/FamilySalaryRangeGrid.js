Ext._define('rh.gfp.familysalary.FamilySalaryRangeGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.gfp.familysalary.FamilySalaryRangeWindow',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Descrição', dataIndex: 'unicode', id: 'autoExpandColumn'},
                    {header: 'Limite Inferior', dataIndex: 'inferior_limit', width: 90, renderer: toolkit.util.formatCurrency},
                    {header: 'Limite Superior', dataIndex: 'upper_limit', width: 90, renderer: toolkit.util.formatCurrency},
                    {header: 'Valor', dataIndex: 'value', width: 90, renderer: toolkit.util.formatCurrency},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'rh.gfp.familysalary.FamilySalaryRangeRestful',
    'rh.gfp.familysalary.FamilySalaryRangeGrid'
);

