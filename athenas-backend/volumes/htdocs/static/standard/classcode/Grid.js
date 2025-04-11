/**
 *
 **/
Ext._define('standard.classcode.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'standard.classcode.Window',

    keywordFieldMessage: 'Texto',

    // remoteColumnModel: true,

    showBoolean: function(value){
        return value ? 'SIM' : 'NÃO'
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Chave', dataIndex: 'pk', width: 55, hidden: true},
                    {header: 'Título', dataIndex: 'title', 'minWidth': 60, id: 'autoExpandColumn'},
                    {header: 'Path', dataIndex: 'path', width: 180},
                    {header: 'slug', dataIndex: 'slug', width: 180},
                    {header: 'Objeto', dataIndex: 'name_object', width: 150},
                    {header: 'Type', dataIndex: 'typeof', width: 150},

                ]
            );

        return this._columnModel;
    },
});

core.RestfulGrid.register(
    'standard.classcode.Restful',
    'standard.classcode.Grid'
);
