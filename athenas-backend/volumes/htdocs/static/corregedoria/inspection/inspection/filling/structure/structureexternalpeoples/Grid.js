Ext._define('corregedoria.inspection.inspection.filling.structure.structureexternalpeoples.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.inspection.inspection.filling.structure.structureexternalpeoples.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Servidor/Membro', dataIndex: 'name', width: 350, },
                    {header: 'Categoria', dataIndex: 'function', width: 350, },
                    {header: 'Função/Cargo', dataIndex: 'category', id: 'autoExpandColumn', },
                ]
            );

        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.inspection.inspection.filling.structure.structureexternalpeoples.Restful',
    'corregedoria.inspection.inspection.filling.structure.structureexternalpeoples.Grid'
);
