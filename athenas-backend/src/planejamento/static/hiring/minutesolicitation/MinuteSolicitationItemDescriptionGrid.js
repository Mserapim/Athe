Ext._define('planning.hiring.minutesolicitation.MinuteSolicitationItemDescriptionGrid', {
    extend: 'core.RestfulGrid',

    rest: 'planning.hiring.minutesolicitation.MinuteSolicitationItemDescriptionRestful',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Cod', dataIndex: 'pk', width: 50, hidden: true},
                    {header: 'Descricao', dataIndex: 'unicode', id: 'autoExpandColumn'},
                    {header: 'Item', dataIndex: 'item_description_unicode', width: 120, id: 'autoExpandColumn'},
                    {header: 'Solicitação', dataIndex: 'item_solicitation_unicode', width: 120},
                ]
            );

        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'planning.hiring.minutesolicitation.MinuteSolicitationItemDescriptionRestful',
    'planning.hiring.minutesolicitation.MinuteSolicitationItemDescriptionGrid'
);

