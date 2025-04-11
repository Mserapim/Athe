Ext._define('rh.gfp.familysalary.FamilySalaryGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.gfp.familysalary.FamilySalaryWindow',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Descrição', dataIndex: 'description', id: 'autoExpandColumn'},
                    {header: 'Início Vigência', dataIndex: 'start_date', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                    {header: 'Fim Vigência', dataIndex: 'end_date', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')},
                    {header: 'Publicação', dataIndex: 'publication_unicode', width: 120},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'rh.gfp.familysalary.FamilySalaryRestful',
    'rh.gfp.familysalary.FamilySalaryGrid'
);

