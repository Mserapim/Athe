Ext._define('judicial.params.ActingZoneGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'judicial.params.ActingZoneWindow',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Descricao', dataIndex: 'title', id: 'autoExpandColumn'},
                    {header: 'Ativo', dataIndex: 'enabled', width: 60, renderer: function(value) { return (value ? 'SIM' : 'NÃO'); }}
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'judicial.params.ActingZoneRestful',
    'judicial.params.ActingZoneGrid'
);

