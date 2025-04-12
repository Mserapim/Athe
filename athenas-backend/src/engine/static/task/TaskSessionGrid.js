/**
 *
 **/
Ext._define('engine.TaskSessionGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'engine.TaskSessionWindow',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Chave', dataIndex: 'pk', width: 55, hidden: true},                    
                    {header: 'SID', dataIndex: 'sid', width: 200},
                    {header: 'User', dataIndex: 'user_unicode', width: 150},
                    {header: 'Start', dataIndex: 'started_task', width: 150},
                    {header: 'Finish', dataIndex: 'finished_task', width: 150},
                    {header: 'Descrição', dataIndex: 'description', id: 'autoExpandColumn'},
                ]
            );

        return this._columnModel;
    },
});

core.RestfulGrid.register(
    'engine.TaskSessionMessageRestful',
    'engine.TaskSessionGrid'
);