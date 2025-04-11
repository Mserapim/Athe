/**
 *
 **/
Ext._define('rh.gfp.estrutura_salarial.CargosEstruturaGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.gfp.estrutura_salarial.CargosEstruturaWindow',

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
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Chave', dataIndex: 'pk', width: 55, hidden: true},
                    // {header: 'Estrutura Salarial', dataIndex: 'estrutura_salarial_unicode', 'minWidth': 150, id: 'autoExpandColumn'},
                    {header: 'Cargo', dataIndex: 'cargo_unicode', minWidth: 150, id: 'autoExpandColumn'},
                    {header: 'Início vigência', dataIndex: 'data_vigencia_inicio', width: 80, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                    {header: 'Fim vigência', dataIndex: 'data_vigencia_fim', width: 80, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                    {header: 'Publicação', dataIndex: 'publicacao_unicode', width: 180},
                ]
            );

        return this._columnModel;
    },
});

core.RestfulGrid.register(
    'rh.gfp.estrutura_salarial.CargosEstruturaRestful',
    'rh.gfp.estrutura_salarial.CargosEstruturaGrid'
);
