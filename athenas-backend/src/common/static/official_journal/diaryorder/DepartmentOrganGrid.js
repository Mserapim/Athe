
Ext._define('common.official_journal.diaryorder.DepartmentOrganGrid', {
    extend: 'core.RestfulGrid',

    rest: 'rh.generalorgan.Restful',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Órgão', dataIndex: 'nome', id: 'autoExpandColumn'}
                ]
            );

        return this._columnModel;
    }

});

core.RestfulGrid.register(
    'rh.generalorgan.Restful',
    'common.official_journal.diaryorder.DepartmentOrganGrid'
);
