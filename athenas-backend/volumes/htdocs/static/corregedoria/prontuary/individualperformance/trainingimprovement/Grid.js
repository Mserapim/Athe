Ext._define('corregedoria.prontuary.individualperformance.trainingimprovement.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.prontuary.individualperformance.trainingimprovement.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 30, renderer: core.rendererIconGrid, menuDisabled: true, },
                    {header: 'Publicação', dataIndex: 'publication', id: 'autoExpandColumn', },
                    // {header: 'Tipo', dataIndex: 'publication_type_unicode', width: 150, },
                    {header: 'Data', dataIndex: 'date_publication', width: 100, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                    {header: 'Pontuação', dataIndex: 'score', width: 90, },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.prontuary.individualperformance.trainingimprovement.Restful',
    'corregedoria.prontuary.individualperformance.trainingimprovement.Grid'
);
