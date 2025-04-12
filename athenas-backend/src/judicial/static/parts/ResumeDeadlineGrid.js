Ext._define('judicial.parts.ResumeDeadlineGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'judicial.parts.ResumeDeadlineWindow',

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
    'judicial.parts.ResumeDeadlineRestful',
    'judicial.parts.ResumeDeadlineGrid'
);
