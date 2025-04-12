Ext._define('raf.subitem.CalculateGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'raf.subitem.CalculateWindow',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'A ser calculado', dataIndex: 'subitem_unicode', id: 'autoExpandColumn', hidden: true},
                    {header: 'Para cálculo', dataIndex: 'from_the_sum_unicode', width: 200},
                    {header: 'Afetar', dataIndex: 'affectation_display', width: 100},
                    {header: '', dataIndex: 'icons', width: 50, renderer: core.rendererIconGrid, menuDisabled: true},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'raf.subitem.CalculateRestful',
    'raf.subitem.CalculateGrid'
);
