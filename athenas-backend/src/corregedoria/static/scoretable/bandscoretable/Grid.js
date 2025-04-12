Ext._define('corregedoria.scoretable.bandscoretable.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.scoretable.bandscoretable.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Descrição', dataIndex: 'label', id: 'autoExpandColumn', },
                    {header: 'Início da Faixa', dataIndex: 'initial_value', width: 150, },
                    {header: 'Final da Faixa', dataIndex: 'end_value', width: 150, },
                    {header: 'Pontuação', dataIndex: 'score', width: 150, },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.scoretable.bandscoretable.Restful',
    'corregedoria.scoretable.bandscoretable.Grid'
);
