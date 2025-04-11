Ext._define('corregedoria.cirdir.teaching.discipline.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.cirdir.teaching.discipline.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Disciplina', dataIndex: 'name', id: 'autoExpandColumn', },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.cirdir.teaching.discipline.Restful',
    'corregedoria.cirdir.teaching.discipline.Grid'
);
