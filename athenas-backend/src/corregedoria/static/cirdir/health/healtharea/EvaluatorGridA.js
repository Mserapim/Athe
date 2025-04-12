Ext._define('corregedoria.cirdir.health.healtharea.EvaluatorGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.cirdir.health.healtharea.EvaluatorWindow',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Nome', dataIndex: 'name', id: 'autoExpandColumn', },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.cirdir.health.healtharea.EvaluatorRestful',
    'corregedoria.cirdir.health.healtharea.EvaluatorGrid'
);
