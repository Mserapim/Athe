/**
 *
 **/
Ext._define('rh.movimentacao.requisicao.PeriodoRequisicaoGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.movimentacao.requisicao.PeriodoRequisicaoWindow',

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
    'rh.movimentacao.requisicao.PeriodoRequisicaoRestful',
    'rh.movimentacao.requisicao.PeriodoRequisicaoGrid'
);
