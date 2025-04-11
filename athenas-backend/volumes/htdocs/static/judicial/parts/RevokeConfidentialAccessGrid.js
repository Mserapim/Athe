
Ext._define('judicial.parts.RevokeConfidentialAccessGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'judicial.parts.RevokeConfidentialAccessWindow',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'created_at', dataIndex: 'dispatch_title', id: 'autoExpandColumn', renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'judicial.parts.RevokeConfidentialAccessRestful',
    'judicial.parts.RevokeConfidentialAccessGrid'
);
