/**
 *
 **/
Ext._define('rh.movimentacao.possession.request.PeriodoRequisicaoGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.movimentacao.possession.request.PeriodoRequisicaoWindow',

    singleton: {
        types: [],
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Publicação', dataIndex: 'publicacao_unicode', id: 'autoExpandColumn'},
                    {header: 'Data início', dataIndex: 'data_inicio', width: 95},
                    {header: 'Data fim', dataIndex: 'data_fim', width: 95},
                ]
            );

        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'rh.movimentacao.possession.request.PeriodoRequisicaoRestful',
    'rh.movimentacao.possession.request.PeriodoRequisicaoGrid'
);
