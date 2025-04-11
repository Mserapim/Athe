Ext._define('judicial.parts.SuspendDeadlineGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'judicial.parts.SuspendDeadlineWindow',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'judicial.parts.SuspendDeadlineRestful',
    'judicial.parts.SuspendDeadlineGrid'
);
