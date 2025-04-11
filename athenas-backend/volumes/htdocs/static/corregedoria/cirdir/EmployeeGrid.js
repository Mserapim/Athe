Ext._define('corregedoria.cirdir.EmployeeGrid', {
    extend: 'rh.employee.Grid',

    rest: 'corregedoria.cirdir.EmployeeRestful',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = new Ext.grid.ColumnModel({
                columns: [
                    {
                      header: 'Matrícula',
                      dataIndex: 'matricula',
                      width: 70,
                      sortable: false,
                      align: 'center',
                      menuDisabled: true,
                    },
                    {
                      header: 'Nome',
                      dataIndex: 'pessoa_fisica_unicode',
                      id: 'autoExpandColumn',
                      sortable: false,
                      menuDisabled: true,
                    },
                ],
            });
        return this._columnModel;
    },


});

core.RestfulGrid.register(
    'corregedoria.cirdir.EmployeeRestful',
    'corregedoria.cirdir.EmployeeGrid'
);
