Ext._define('rh.telefone.emergency.Grid', {
    extend: 'rh.telefone.TelefoneGrid',
    restWindow: 'rh.telefone.emergency.Window',
    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Número', dataIndex: 'numero', width: 125, sortable: true},
                    {header: 'Nome/Contato de Emergência', dataIndex: 'description', id: 'autoExpandColumn', sortable: true, hidden: false},
                    {header: 'Parentesco', dataIndex: 'kinship', width: 120, sortable: true},
                    {header: 'Tipo', dataIndex: 'tipo_telefone_display', width: 142, sortable: true},
                    {header: 'Principal', dataIndex: 'main', width: 66, renderer: function(value) { return (value ? 'SIM' : 'NÃO'); }, hidden: false},
                    {header: 'Público', dataIndex: 'publico', width: 66, renderer: function(value) { return (value ? 'SIM' : 'NÃO'); }, sortable: true},
                    {header: 'Criado por', dataIndex: 'created_by_unicode', width: 120, sortable: true, hidden: true},
                    {header: 'Criado em', dataIndex: 'created_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), sortable: true, hidden: true},
                    {header: 'Modificado por', dataIndex: 'modified_by_unicode', width: 120, sortable: true, hidden: true},
                    {header: 'Modificado em', dataIndex: 'modified_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), sortable: true, hidden: true},
                ]
            );           

        return this._columnModel;
    },

    
});
core.RestfulGrid.register(
    'rh.telefone.emergency.Restful',
    'rh.telefone.emergency.Grid'
);
