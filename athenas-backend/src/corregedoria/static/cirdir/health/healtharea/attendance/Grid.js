Ext._define('corregedoria.cirdir.health.healtharea.attendance.Grid', {
    extend: 'core.RestfulGrid',

    rest: 'corregedoria.cirdir.health.healtharea.attendance.Restful',

    configOrderToolBar: ['add', 'edit', 'remove', ],


    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Questionários', dataIndex: 'evaluate_unicode', id: 'autoExpandColumn', },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.cirdir.health.healtharea.attendance.Restful',
    'corregedoria.cirdir.health.healtharea.attendance.Grid'
);
