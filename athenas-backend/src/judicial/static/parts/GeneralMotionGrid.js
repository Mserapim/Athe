Ext._define('judicial.parts.GeneralMotionGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'judicial.parts.GeneralMotionWindow',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Descrição', dataIndex: 'unicode', id: 'autoExpandColumn'},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'judicial.parts.GeneralMotionRestful',
    'judicial.parts.GeneralMotionGrid'
);
