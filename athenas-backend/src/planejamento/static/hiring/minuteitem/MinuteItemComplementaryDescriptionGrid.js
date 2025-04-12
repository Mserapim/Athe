Ext._define('planning.hiring.minuteitem.MinuteItemComplementaryDescriptionGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'planning.hiring.minuteitem.MinuteItemComplementaryDescriptionWindow',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),                    
                    {header: 'Característica', dataIndex: 'characteristic', width: 90},
                    {header: 'Descrição', dataIndex: 'description', id: 'autoExpandColumn'},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'planning.hiring.minuteitem.MinuteItemComplementaryDescriptionRestful',
    'planning.hiring.minuteitem.MinuteItemComplementaryDescriptionGrid'
);
