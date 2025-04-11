Ext._define('common.document_access.log.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'common.document_access.log.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Cód.', dataIndex: 'pk', width: 50, hidden: true},
                    {header: 'Descricao', dataIndex: 'unicode', width: 120, hidden: true},
                    {header: 'Tipo ação', dataIndex: 'log_type_display', width: 95},
                    {header: 'Responsável', dataIndex: 'signed_by_unicode', id: 'autoExpandColumn'},
                    {header: 'Data ação', dataIndex: 'signed_at', width: 100, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')},
                    {header: 'Documento', dataIndex: 'control_unicode', width: 120},
                    {header: 'Nível de acesso', dataIndex: 'control_type_unicode', width: 120}
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'common.document_access.log.Restful',
    'common.document_access.log.Grid'
);
