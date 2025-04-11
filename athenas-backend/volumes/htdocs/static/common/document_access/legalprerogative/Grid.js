Ext._define('common.document_access.legalprerogative.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'common.document_access.legalprerogative.Window',

    getColumnModel: function() {
        if (!this._columnModel) {
            this._columnModel = Ext._create('Ext.grid.ColumnModel', [
                Ext._create('Ext.grid.RowNumberer'),
                {header: 'Cód.', dataIndex: 'pk', width: 50},
                {header: 'Título', dataIndex: 'title', id: 'autoExpandColumn'},
                {header: 'Descrição', dataIndex: 'unicode', width: 90},
                {header: 'Nível de acesso', dataIndex: 'control_type_unicode', width: 120},
                {header: 'Habilitado', dataIndex: 'enabled', width: 90, renderer: function(value) { return (value ? 'SIM' : 'NÃO'); }},
                {header: 'Criado por', dataIndex: 'created_by_unicode', width: 120},
                {header: 'Criado em', dataIndex: 'created_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')},
                {header: 'Modificado por', dataIndex: 'modified_by_unicode', width: 120},
                {header: 'Modificado em', dataIndex: 'modified_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')},
            ]);
        }

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'common.document_access.legalprerogative.Restful',
    'common.document_access.legalprerogative.Grid'
);
