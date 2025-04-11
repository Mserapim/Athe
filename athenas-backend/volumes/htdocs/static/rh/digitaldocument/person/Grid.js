Ext._define('rh.digitaldocument.person.Grid', {
    extend: 'rh.digitaldocument.Grid',
    restWindow: 'rh.digitaldocument.person.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Tipo', dataIndex: 'document_type_display', width: 120, hidden: false},
                    {header: 'Arquivo', dataIndex: 'file_unicode', id: 'autoExpandColumn', hidden: false},
                    {header: 'Nome', dataIndex: 'name', width: 100, hidden: true},
                    {header: 'Criado por', dataIndex: 'created_by_unicode', width: 120, hidden: true},
                    {header: 'Criado em', dataIndex: 'created_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), hidden: true},
                    {header: 'Modificado por', dataIndex: 'modified_by_unicode', width: 120, hidden: true},
                    {header: 'Modificado em', dataIndex: 'modified_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), hidden: true},
                    {header: 'Servidor', dataIndex: 'employee_unicode', width: 120, hidden: true},
                    {header: 'Data Início', dataIndex: 'date_start', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), hidden: true},
                    {header: 'Data Fim', dataIndex: 'date_end', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), hidden: true},
                    {header: 'Documento', dataIndex: 'document__person_unicode', width: 120, hidden: true},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'rh.digitaldocument.person.Restful',
    'rh.digitaldocument.person.Grid'
);
