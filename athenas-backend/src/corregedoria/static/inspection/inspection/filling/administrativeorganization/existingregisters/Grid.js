Ext._define('corregedoria.inspection.inspection.filling.administrativeorganization.existingregisters.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.inspection.inspection.filling.administrativeorganization.existingregisters.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Registro', dataIndex: 'register', id: 'autoExpandColumn', },
                    {header: 'Tipo', dataIndex: 'registration_type_display', width: 150, },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.inspection.inspection.filling.administrativeorganization.existingregisters.Restful',
    'corregedoria.inspection.inspection.filling.administrativeorganization.existingregisters.Grid'
);
