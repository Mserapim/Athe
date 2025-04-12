Ext._define('raf.EmployeeGrid', {
    extend: 'rh.employee.Grid',

    rest: 'raf.EmployeeRestful',

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
                    {
                      header: 'Data',
                      dataIndex: 'first_adjustment_date',
                      width: 125,
                      sortable: false,
                      // renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'),
                      menuDisabled: true,
                    },
                ],
            });
        return this._columnModel;
    },


});

core.RestfulGrid.register(
    'raf.EmployeeRestful',
    'raf.EmployeeGrid'
);
