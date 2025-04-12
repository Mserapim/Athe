Ext._define('edocs.protocolo.requestform.dependent.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'edocs.protocolo.requestform.dependent.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Cod', dataIndex: 'pk', width: 50, hidden: true},
                    {header: 'Unicode', dataIndex: 'unicode', width: 120, hidden: true},
                    {header: 'Content Type', dataIndex: 'content_type_unicode', width: 120, hidden: true},
                    {header: 'Object id', dataIndex: 'object_id', width: 90, hidden: true},
                    {header: 'Nome', dataIndex: 'name', width: 180},
                    {header: 'CPF', dataIndex: 'cpf', width: 90},
                    {header: 'Grau de Parentesco', dataIndex: 'degree_of_kinship_display', id: 'autoExpandColumn'},
                    {header: 'Desimpedido', dataIndex: 'unimpeded_as_taxpayer_dependent', width: 80, renderer: function(value) { return (value ? 'SIM' : 'NÃO'); }}
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.dependent.Restful',
    'edocs.protocolo.requestform.dependent.Grid'
);
