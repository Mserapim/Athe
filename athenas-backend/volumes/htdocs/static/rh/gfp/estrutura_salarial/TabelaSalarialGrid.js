/**
 *
 **/
Ext._define('rh.gfp.estrutura_salarial.TabelaSalarialGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.gfp.estrutura_salarial.TabelaSalarialWindow',

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
                    {header: 'Início vigência', dataIndex: 'start_validity', width: 80, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                    {header: 'Fim vigência', dataIndex: 'end_validity', width: 80, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                    {header: 'Informação', dataIndex: 'info_adicional', width: 90},
                    {header: 'Publicação', dataIndex: 'publicacao_unicode', minWidth: 180, id: 'autoExpandColumn'},
                    {header: 'Estrutura Salarial', dataIndex: 'estrutura_salarial_unicode', 'minWidth': 150},
                    {header: 'Tabela anterior', dataIndex: 'tabela_anterior_unicode', width: 250},
                ]
            );

        return this._columnModel;
    },

    copyItem: function(values) {
        console.debug(values);
        Ext.apply(values,{
            tabela_anterior: values.pk,
            tabela_anterior_unicode: values.unicode,
            publicacao: undefined,
            start_validity: undefined,
            end_validity: undefined,
            percentual: 0
        });
        this.createItem(values);
    },

});

core.RestfulGrid.register(
    'rh.gfp.estrutura_salarial.TabelaSalarialRestful',
    'rh.gfp.estrutura_salarial.TabelaSalarialGrid'
);
