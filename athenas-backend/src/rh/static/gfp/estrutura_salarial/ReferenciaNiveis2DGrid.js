/**
 *
 **/
Ext._define('rh.gfp.estrutura_salarial.ReferenciaNiveis2DGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.gfp.estrutura_salarial.ReferenciaNiveis2DWindow',

    keywordFieldMessage: 'Texto',

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
                    {header: 'Ordem', dataIndex: 'ordem', width: 80},
                    {header: 'Estrutura Salarial', dataIndex: 'estrutura_salarial_unicode', 'minWidth': 240, id: 'autoExpandColumn'},
                    {header: 'Vertical', dataIndex: 'vertical', width: 80},
                    {header: 'Horizontal', dataIndex: 'horizontal', width: 80},
                    {header: 'Meses progressão', dataIndex: 'months_progression', width: 80},
                    {header: 'Valor Servidor', dataIndex: 'tipo_valor_display', width: 100},
                    {header: 'Gratif. Servidor', dataIndex: 'tipo_gratificacao_display', width: 100},
                    {header: 'Valor Membro', dataIndex: 'tipo_valor_membro_display', width: 100},
                    {header: 'Gratif. Membro', dataIndex: 'tipo_gratificacao_membro_display', width: 100},
                    {header: 'Ativo', dataIndex: 'ativo', width: 80, renderer: this.showBoolean},
                    {header: 'Referência anterior', dataIndex: 'referencia_anterior_unicode', width: 80},
                    {header: 'Fator', dataIndex: 'fator_atualizacao', width: 80},
                ]
            );

        return this._columnModel;
    },
});

core.RestfulGrid.register(
    'rh.gfp.estrutura_salarial.ReferenciaNiveis2DRestful',
    'rh.gfp.estrutura_salarial.ReferenciaNiveis2DGrid'
);
