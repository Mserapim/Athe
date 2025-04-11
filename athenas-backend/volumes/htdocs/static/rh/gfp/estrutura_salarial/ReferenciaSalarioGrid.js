/**
 *
 **/
Ext._define('rh.gfp.estrutura_salarial.ReferenciaSalarioGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.gfp.estrutura_salarial.ReferenciaSalarioWindow',

    keywordFieldMessage: 'Texto',

    hideItemsToolbar: ['edit', 'remove'],

    showBoolean: function(value){
        return value ? 'SIM' : 'NÃO'
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    // Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Chave', dataIndex: 'pk', width: 55, hidden: true},
                    {header: 'Tabela salarial', dataIndex: 'tabela_salarial_unicode', minWidth: 150, id: 'autoExpandColumn'},
                    {header: 'Sigla', dataIndex: 'sigla_cache', width: 60},
                    {header: 'Valor Servidor', dataIndex: 'valor', width: 80, renderer: toolkit.util.formatCurrency},
                    {header: 'Gratif. Servidor', dataIndex: 'gratificacao', width: 80, renderer: toolkit.util.formatCurrency},
                    {header: 'Valor Membro', dataIndex: 'valor_membro', width: 80, renderer: toolkit.util.formatCurrency},
                    {header: 'Gratif. Membro', dataIndex: 'gratificacao_membro', width: 80, renderer: toolkit.util.formatCurrency},
                ]
            );

        return this._columnModel;
    },
});

core.RestfulGrid.register(
    'rh.gfp.estrutura_salarial.ReferenciaSalarioRestful',
    'rh.gfp.estrutura_salarial.ReferenciaSalarioGrid'
);
