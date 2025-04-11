Ext._define('corregedoria.prontuary.career.others.availability.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.prontuary.career.others.availability.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 30, renderer: core.rendererIconGrid, menuDisabled: true, },
                    {header: 'Exercício', dataIndex: 'exercise', id: 'autoExpandColumn', },
                    // {header: 'Pontuação', dataIndex: 'score', width: 90, },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.prontuary.career.others.availability.Restful',
    'corregedoria.prontuary.career.others.availability.Grid'
);
