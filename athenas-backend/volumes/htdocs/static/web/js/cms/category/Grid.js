
Ext._define('web.cms.category.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'web.cms.category.Window',
    hideItemsToolbar: ['edit', 'download'],
    hideActions: ['copy'],
    keywordFieldMessage: 'Digite o termo para busca e tecle Enter',
    actionColumnWidth: 50,

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Categoria', dataIndex: 'path', id: 'autoExpandColumn'}
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'web.cms.category.Restful',
    'web.cms.category.Grid'
);