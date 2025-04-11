 Ext._define('rh.highereducationinstitution.HigherEducationInstitutionGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.highereducationinstitution.HigherEducationInstitutionWindow',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Código', dataIndex: 'code', width: 90},
                    {header: 'Nome', dataIndex: 'name', id: 'autoExpandColumn'},
                    {header: 'Sigla', dataIndex: 'acronym', width: 120},
                    {header: 'Município', dataIndex: 'municipality_unicode', width: 120},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'rh.highereducationinstitution.HigherEducationInstitutionRestful',
    'rh.highereducationinstitution.HigherEducationInstitutionGrid'
);

