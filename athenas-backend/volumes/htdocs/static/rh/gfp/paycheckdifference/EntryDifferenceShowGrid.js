Ext._define('rh.gfp.paycheckdifference.EntryDifferenceShowGrid', {
    extend: 'core.RestfulGrid',

    rest: 'rh.gfp.paycheckdifference.EntryShowRestful',

    configOrderToolBar: ['search'],

    hideActions: ['add', 'copy', 'remove', 'edit'],

    
    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    // {header: 'Contra-Cheque', dataIndex: 'contracheque_unicode', id: 'autoExpandColumn'},
                    {header: 'Referência', dataIndex: 'reference', width: 150},                    
                    {header: 'Evento', dataIndex: 'unicode', width: 300, id: 'autoExpandColumn'},
                    {header: 'Valor', dataIndex: 'value', width: 80, renderer: toolkit.util.formatCurrency},
                    {header: 'Patronal (R$)', dataIndex: 'employer_contribution', width: 90, renderer: toolkit.util.formatCurrency},
                ]
            );

        return this._columnModel;
    }

});

core.RestfulGrid.register(
    'rh.gfp.paycheckdifference.EntryShowRestful',
    'rh.gfp.paycheckdifference.EntryDifferenceShowGrid'
);