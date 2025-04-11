Ext._define('corregedoria.inspection.inspection.filling.recommendations.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.inspection.inspection.filling.recommendations.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    { header: 'Recomendação', dataIndex: 'recommendation', id: 'autoExpandColumn', },
                    {header: 'Prazo', dataIndex: 'deadline_grid', width: 70},
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.inspection.inspection.filling.recommendations.Restful',
    'corregedoria.inspection.inspection.filling.recommendations.Grid'
);
