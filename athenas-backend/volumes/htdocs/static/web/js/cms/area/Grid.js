
Ext._define('web.cms.area.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'web.cms.area.Window',
    hideItemsToolbar: ['edit', 'download'],
    hideActions: ['copy', 'edit'],
    keywordFieldMessage: 'Digite o termo para busca e tecle Enter',
    actionColumnWidth: 35,

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Nome', dataIndex: 'fullname', id: 'autoExpandColumn'},
                    {header: 'Conteúdo', dataIndex: 'kind_of_content_display'},
                    {header: 'Site', dataIndex: 'parent_unicode', width: 200, renderer: function(val) {
                        return val || '[Site]';
                    }},
                    {header: 'Pode compartilhar?', dataIndex: 'can_share', width: 120, renderer: function(val) {
                        return (val) ? 'Sim': 'Não';
                    }}
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'web.cms.area.Restful',
    'web.cms.area.Grid'
);