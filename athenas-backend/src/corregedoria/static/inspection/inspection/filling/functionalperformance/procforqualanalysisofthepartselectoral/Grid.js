Ext._define('corregedoria.inspection.inspection.filling.functionalperformance.procforqualanalysisofthepartselectoral.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.inspection.inspection.filling.functionalperformance.procforqualanalysisofthepartselectoral.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Tipo de Ação', dataIndex: 'action_type_title', width: 250, },
                    {header: 'Número do Feito', dataIndex: 'action_number', width: 250, },
                    {header: 'Tipo de Peça', dataIndex: 'part_type_title', id: 'autoExpandColumn', },
                    {header: 'Pontuação', dataIndex: 'score', width: 150, },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.inspection.inspection.filling.functionalperformance.procforqualanalysisofthepartselectoral.Restful',
    'corregedoria.inspection.inspection.filling.functionalperformance.procforqualanalysisofthepartselectoral.Grid'
);
