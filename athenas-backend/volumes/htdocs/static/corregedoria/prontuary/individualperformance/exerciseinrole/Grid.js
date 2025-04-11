Ext._define('corregedoria.prontuary.individualperformance.exerciseinrole.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.prontuary.individualperformance.exerciseinrole.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 30, renderer: core.rendererIconGrid, menuDisabled: true, },
                    {header: 'Exercício', dataIndex: 'exercise', id: 'autoExpandColumn', },
                    {header: 'Pontuação', dataIndex: 'score', width: 90, },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.prontuary.individualperformance.exerciseinrole.Restful',
    'corregedoria.prontuary.individualperformance.exerciseinrole.Grid'
);
