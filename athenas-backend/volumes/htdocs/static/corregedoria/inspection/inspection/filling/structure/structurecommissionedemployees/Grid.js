Ext._define('corregedoria.inspection.inspection.filling.structure.structurecommissionedemployees.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.inspection.inspection.filling.structure.structurecommissionedemployees.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Servidor/Membro', dataIndex: 'sce_employee_unicode', width: 450, },
                    {header: 'Função/Cargo', dataIndex: 'sce_occupation_unicode', id: 'autoExpandColumn', },
                ]
            );

        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.inspection.inspection.filling.structure.structurecommissionedemployees.Restful',
    'corregedoria.inspection.inspection.filling.structure.structurecommissionedemployees.Grid'
);
