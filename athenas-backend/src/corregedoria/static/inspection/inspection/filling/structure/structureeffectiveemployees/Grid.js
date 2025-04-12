Ext._define('corregedoria.inspection.inspection.filling.structure.structureeffectiveemployees.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.inspection.inspection.filling.structure.structureeffectiveemployees.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Servidor/Membro', dataIndex: 'sef_employee_unicode', width: 450, },
                    {header: 'Função/Cargo', dataIndex: 'sef_occupation_unicode', id: 'autoExpandColumn', },
                ]
            );

        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.inspection.inspection.filling.structure.structureeffectiveemployees.Restful',
    'corregedoria.inspection.inspection.filling.structure.structureeffectiveemployees.Grid'
);
