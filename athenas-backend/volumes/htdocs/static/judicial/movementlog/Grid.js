Ext._define('judicial.movementlog.Grid', {
    extend: 'core.RestfulGrid',
    restWindow: 'judicial.movementlog.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Procedimento', dataIndex: 'out_court_lawsuit_unicode', hidden: true},
                    {header: 'Origem', dataIndex: 'from_location_unicode', id: 'autoExpandColumn'},
                    {header: 'Enviado por', dataIndex: 'sended_by_unicode'},
                    {header: 'Enviado em', dataIndex: 'sended_at', renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), width: 120},
                    {header: 'Destino', dataIndex: 'to_location_unicode'},
                    {header: 'Recebido por', dataIndex: 'received_by_unicode'},
                    {header: 'Recebido em', dataIndex: 'received_at', renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), width: 120},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'judicial.movementlog.Restful',
    'judicial.movementlog.Grid'
);
