Ext._define('corregedoria.cirdir.teaching.institution.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.cirdir.teaching.institution.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Insituição', dataIndex: 'razao_social', id: 'autoExpandColumn' },
                    {header: 'Localidade', dataIndex: 'county_unicode', width: 100, },
                    {header: 'CNPJ', dataIndex: 'cnpj', width: 100, },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.cirdir.teaching.institution.Restful',
    'corregedoria.cirdir.teaching.institution.Grid'
);
