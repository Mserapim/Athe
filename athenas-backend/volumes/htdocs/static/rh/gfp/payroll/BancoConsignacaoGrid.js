Ext._define('rh.gfp.payroll.BancoConsignacaoGrid', {
    extend: 'core.RestfulGrid',

    rest: 'rh.gfp.payroll.BancoConsignacaoRestful',

    configOrderToolBar: ['search', ],
    
    hideActions: ['add', 'edit', 'remove'],

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Chave', dataIndex: 'id', width: 50, hidden: true},
                    {header: 'Nome', dataIndex: 'nome', id: 'autoExpandColumn'},
                    {header: 'Número', dataIndex: 'numero', width: 90},
                    {header: 'Agência', dataIndex: 'agencia', width: 90},
                    {header: 'DV Agência', dataIndex: 'dv_agencia', width: 90},
                    {header: 'Conta', dataIndex: 'conta', width: 90},
                    {header: 'DV Conta', dataIndex: 'dv_conta', width: 90},
                ]
            );

        return this._columnModel;
    },
});

core.RestfulGrid.register(
    'rh.gfp.payroll.BancoConsignacaoRestful',
    'rh.gfp.payroll.BancoConsignacaoGrid'
);

