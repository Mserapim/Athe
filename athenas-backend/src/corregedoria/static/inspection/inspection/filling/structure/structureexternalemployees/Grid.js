Ext._define('corregedoria.inspection.inspection.filling.structure.structureexternalemployees.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.inspection.inspection.filling.structure.structureexternalemployees.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Servidor/Membro', dataIndex: 'see_employee_unicode', width: 350, },
                    {header: 'Categoria', dataIndex: 'see_category', width: 350, },
                    {header: 'Função/Cargo', dataIndex: 'see_occupation_unicode', id: 'autoExpandColumn', },
                ]
            );

        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.inspection.inspection.filling.structure.structureexternalemployees.Restful',
    'corregedoria.inspection.inspection.filling.structure.structureexternalemployees.Grid'
);
