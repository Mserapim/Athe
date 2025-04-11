
Ext._define('web.cms.contentarea.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'web.cms.contentarea.Window',
    hideItemsToolbar: ['edit', 'download'],
    hideActions: ['copy', 'edit'],
    keywordFieldMessage: 'Digite o termo para busca e tecle Enter',
    actionColumnWidth: 35,

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Area', dataIndex: 'area'},
                    {header: 'Conteúdo', dataIndex: 'content', id: 'autoExpandColumn'},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'web.cms.contentarea.Restful',
    'web.cms.contentarea.Grid'
);