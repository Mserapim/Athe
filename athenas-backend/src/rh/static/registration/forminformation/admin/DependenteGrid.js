Ext._define('rh.registration.forminformation.admin.DependenteGrid', {
    extend: 'core.RestfulGrid',

    rest: 'rh.registration.forminformation.admin.DependenteRestful',
    restWindow: 'rh.registration.forminformation.admin.DependenteWindow',
        
    hideItemsToolbar: ['add', 'remove', 'search', 'download'],
    hideActions: ['remove', 'copy'],
    
    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Nome', dataIndex: 'nome_dependent', id: 'autoExpandColumn',  width: 45},
                    {header: 'CPF', dataIndex: 'cpf_dependent', width: 90},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'rh.registration.forminformation.admin.DependenteRestful',
    'rh.registration.forminformation.admin.DependenteGrid'
);

