
Ext._define('judicial.remittance.RemittanceItselfOrganGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'judicial.remittance.RemittanceItselfOrganWindow',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Descricao', dataIndex: 'unicode', id: 'autoExpandColumn'},
                    {header: 'type part', dataIndex: 'type_part', width: 90},
                    {header: 'partlawsuit ptr', dataIndex: 'partlawsuit_ptr', width: 90},
                    {header: 'text', dataIndex: 'text', width: 90},
                    {header: 'cache rendered', dataIndex: 'cache_rendered', width: 90},
                    {header: 'lawsuit', dataIndex: 'lawsuit_unicode', width: 120},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'judicial.remittance.RemittanceItselfOrganRestful',
    'judicial.remittance.RemittanceItselfOrganGrid'
);

