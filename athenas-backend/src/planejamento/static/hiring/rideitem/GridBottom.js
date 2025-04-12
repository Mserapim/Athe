Ext._define('planning.hiring.rideitem.GridBottom', {
    extend: 'planning.hiring.rideitem.Grid',

    getColumnModel: function() {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel', [
                    Ext._create('Ext.grid.RowNumberer'),
                    { header: 'Grupo', dataIndex: 'group', sortable: true, width: 50 },
                    { header: 'Linha', dataIndex: 'line', sortable: true, width: 50 },
                    { header: 'Descrição', dataIndex: 'item_unicode', sortable: true, width: 500},
                    { header: 'Quantidade', dataIndex: 'amount', sortable: true, width: 80 },
                    { header: 'Valor Unitário', dataIndex: 'unitary_value', renderer: toolkit.util.formatCurrency, sortable: true, width: 100 },
                    { header: 'Valor Total', dataIndex: 'total_value', renderer: toolkit.util.formatCurrency, sortable: true, menuDisabled: true, with: 100},
                    { header: 'Status', dataIndex: 'status_display', sortable: true, width: 100 },
                    { header: 'Justificativa (Cancelado)', dataIndex: 'justification', sortable: true, id: 'autoExpandColumn'},
                ]
            );
        return this._columnModel;
    },
});
