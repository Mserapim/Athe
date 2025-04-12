Ext._define('edocs.protocolo.requestform.dependentexclusionitem.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'edocs.protocolo.requestform.dependentexclusionitem.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Cod', dataIndex: 'pk', width: 50, hidden: true},
                    {header: 'Descrição', dataIndex: 'unicode', width: 120, hidden: true},
                    {header: 'Dependente', dataIndex: 'dependent_unicode', id: 'autoExpandColumn'},
                    {header: 'Exclusão', dataIndex: 'dependent_exclusion_unicode', width: 120, hidden: true},
                    {header: 'Imposto de Renda', dataIndex: 'income_tax', width: 120, renderer: function(value) { return (value ? 'SIM' : 'NÃO'); }},
                    {header: 'Pensão Post Mortem', dataIndex: 'post_mortem_pension', width: 120, renderer: function(value) { return (value ? 'SIM' : 'NÃO'); }}
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.dependentexclusionitem.Restful',
    'edocs.protocolo.requestform.dependentexclusionitem.Grid'
);
