/**
 *
 **/
Ext._define('rh.gfp.estrutura_salarial.EstruturaSalarialGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.gfp.estrutura_salarial.EstruturaSalarialWindow',

    keywordFieldMessage: 'Texto',

    remoteColumnModel: true,

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
                    {header: 'Código', dataIndex: 'codigo', width: 80},
                    {header: 'Título', dataIndex: 'titulo', 'minWidth': 240, id: 'autoExpandColumn'},
                    {header: 'Progressão inicial', dataIndex: 'meses_progressao_inicial', width: 80},
                    {header: 'Progressôes', dataIndex: 'meses_progressao', width: 80},
                    // {header: 'Publicação', dataIndex: 'publicacao_unicode', width: 150},
                ]
            );

        return this._columnModel;
    },
});

core.RestfulGrid.register(
    'rh.gfp.estrutura_salarial.EstruturaSalarialRestful',
    'rh.gfp.estrutura_salarial.EstruturaSalarialGrid'
);
