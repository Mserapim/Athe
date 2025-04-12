Ext._define('auth.jwt.VoucherGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'auth.jwt.VoucherWindow',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer', {dataIndex: 'numberer'}),
                    {header: 'Pk', dataIndex: 'pk', width: 50, hidden: true},
                    {header: 'Descrição', dataIndex: 'unicode', width: 90},
                    {header: 'Tipo', dataIndex: 'voucher_type_display', width: 120},
                    {header: 'Usuário', dataIndex: 'user_unicode', width: 120},
                    {header: 'Token', dataIndex: 'token', id: 'autoExpandColumn'},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'auth.jwt.VoucherRestful',
    'auth.jwt.VoucherGrid'
);
