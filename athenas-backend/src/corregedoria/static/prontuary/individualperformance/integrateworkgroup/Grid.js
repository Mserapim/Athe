Ext._define('corregedoria.prontuary.individualperformance.integrateworkgroup.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.prontuary.individualperformance.integrateworkgroup.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    // {header: '', dataIndex: 'icons', width: 30, renderer: core.rendererIconGrid, menuDisabled: true, },
                    {header: 'Grupo de Trabalho', dataIndex: 'workgroup', id: 'autoExpandColumn', },
                    {header: 'Pontuação', dataIndex: 'score', width: 100, },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.prontuary.individualperformance.integrateworkgroup.Restful',
    'corregedoria.prontuary.individualperformance.integrateworkgroup.Grid'
);
