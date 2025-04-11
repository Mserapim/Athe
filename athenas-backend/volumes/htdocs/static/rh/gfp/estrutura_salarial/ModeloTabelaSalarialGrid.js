/**
 *
 **/
Ext._define('rh.gfp.estrutura_salarial.ModeloTabelaSalarialGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.gfp.estrutura_salarial.ModeloTabelaSalarialWindow',

    keywordFieldMessage: 'Texto',

    // remoteColumnModel: true,

    showBoolean: function(value){
        return value ? 'SIM' : 'NÃO'
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Chave', dataIndex: 'pk', width: 55, hidden: true},
                    {header: 'Título', dataIndex: 'titulo', 'minWidth': 60, id: 'autoExpandColumn'},
                    {header: 'Horizontal', dataIndex: 'titulo_horizontal', width: 90},
                    {header: 'Vertical', dataIndex: 'titulo_vertical', width: 90},
                    {header: 'Qtd. Horizontal', dataIndex: 'quantidade_horizontal', width: 70},
                    {header: 'Qtd. Vertical', dataIndex: 'quantidade_vertical', width: 70},
                ]
            );

        return this._columnModel;
    },
});

core.RestfulGrid.register(
    'rh.gfp.estrutura_salarial.ModeloTabelaSalarialRestful',
    'rh.gfp.estrutura_salarial.ModeloTabelaSalarialGrid'
);
