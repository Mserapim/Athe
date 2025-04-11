Ext._define('raf.trustrelationship.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'raf.trustrelationship.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 50, renderer: core.rendererIconGrid, menuDisabled: true},
                    {header: 'Servidor', dataIndex: 'trust_employee_unicode', id: 'autoExpandColumn'},
                    {header: 'Membro', dataIndex: 'employee_unicode', width: 200, hidden: true},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'raf.trustrelationship.Restful',
    'raf.trustrelationship.Grid'
);
