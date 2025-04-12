/**
 *
 **/
Ext._define('rh.movimentacao.requisicao.EncargoFinanceiroGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.movimentacao.requisicao.EncargoFinanceiroWindow',

    singleton: {
        types: [],
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Remuneração', dataIndex: 'remuneracao', id: 'autoExpandColumn'},
                    {header: 'Base previdenciária', dataIndex: 'base_previdenciaria', width: 130},
                    {header: 'Data início', dataIndex: 'data_inicio', width: 80},
                    {header: 'Data fim', dataIndex: 'data_fim', width: 80},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'rh.movimentacao.requisicao.EncargoFinanceiroRestful',
    'rh.movimentacao.requisicao.EncargoFinanceiroGrid'
);
