/**
 *
 **/
Ext._define('rh.movimentacao.requisicao.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.movimentacao.requisicao.Window',

    singleton: {
        types: [],
    },

    constructor: function(cfg) {
        rh.movimentacao.requisicao.Grid.superclass.constructor.call(this, cfg);
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Cod.', dataIndex: 'pk', width: 50},
                    {header: 'Servidor', dataIndex: 'posse_origem_unicode', id: 'autoExpandColumn'},
                    {header: 'Origem', dataIndex: 'orgao_origem_unicode'},
                    {header: 'Data início', dataIndex: 'data_inicio', width: 95},
                    {header: 'Data fim', dataIndex: 'data_fim', width: 95},
                    {header: 'Publicação', dataIndex: 'publicacao_movimentacao_unicode',},
                    {header: 'Ônus', dataIndex: 'onus_display',},
                    {header: 'Categoria Origem(esocial)', dataIndex: 'category_display',},
                    {header: 'Pub. Alteração', dataIndex: 'publicacao_alteracao_unicode', hidden: true},
                    {header: 'Anota', dataIndex: 'anota', renderer: function(v){ return v ? 'Sim' : 'Não'}, width: 60,
                        hidden: true}
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'rh.movimentacao.requisicao.Restful',
    'rh.movimentacao.requisicao.Grid'
);
