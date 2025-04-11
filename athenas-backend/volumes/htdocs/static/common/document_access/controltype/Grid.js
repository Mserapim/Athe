Ext._define('common.document_access.controltype.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'common.document_access.controltype.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Cod', dataIndex: 'pk', width: 50},
                    {header: 'Título', dataIndex: 'title', id: 'autoExpandColumn'},
                    {header: 'Sigiloso?', dataIndex: 'is_secret', width: 90, renderer: function(value) { return (value ? 'SIM' : 'NÃO'); }},
                    {header: 'Permissão necessária', dataIndex: 'required_permission_unicode', width: 220},
                    {header: 'Máx. Aditamentos', dataIndex: 'quantity', width: 105},
                    {header: 'Peso', dataIndex: 'weight', width: 50},
                    {
                        header: 'Prazo máximo',
                        dataIndex: 'max_period',
                        width: 110,
                        sortable: true,
                        renderer: function(value) {
                            return [
                                '<div style="text-align: center">',
                                    (value == 0 ?
                                        '<span style="font-size: 1.5rem">&infin;</span>' :
                                        value
                                    ),
                                '</div>'
                            ].join('')
                        }
                    },
                    {header: 'Desautoriza acesso da comissão?', dataIndex: 'not_allow_admin_access', width: 175, renderer: function(value) { return (value ? 'SIM' : 'NÃO'); }},
                    {header: 'Habilitado', dataIndex: 'enabled', width: 90, renderer: function(value) { return (value ? 'SIM' : 'NÃO'); }},
                    {header: 'Criado por', dataIndex: 'created_by_unicode', width: 120},
                    {header: 'Criado em', dataIndex: 'created_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')},
                    {header: 'Modificado por', dataIndex: 'modified_by_unicode', width: 120},
                    {header: 'Modificado em', dataIndex: 'modified_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'common.document_access.controltype.Restful',
    'common.document_access.controltype.Grid'
);
