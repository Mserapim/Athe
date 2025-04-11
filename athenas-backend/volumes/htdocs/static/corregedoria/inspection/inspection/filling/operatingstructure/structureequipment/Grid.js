Ext._define('corregedoria.inspection.inspection.filling.operatingstructure.structureequipment.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.inspection.inspection.filling.operatingstructure.structureequipment.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Equipamento', dataIndex: 'equipment', id: 'autoExpandColumn', },
                    {header: 'Quantidade', dataIndex: 'amount', width: 100, },
                    {header: 'Estado', dataIndex: 'status_display', width: 250, },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.inspection.inspection.filling.operatingstructure.structureequipment.Restful',
    'corregedoria.inspection.inspection.filling.operatingstructure.structureequipment.Grid'
);
