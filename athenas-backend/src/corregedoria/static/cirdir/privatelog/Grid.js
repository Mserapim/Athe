Ext._define('corregedoria.cirdir.privatelog.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.cirdir.privatelog.Window',

    configOrderToolBar: ['add', 'edit', 'remove', ],

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Data', dataIndex: 'create', width: 120, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i:s')},
                    {header: 'Log Privado', dataIndex: 'information', id: 'autoExpandColumn', },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.cirdir.privatelog.Restful',
    'corregedoria.cirdir.privatelog.Grid'
);
