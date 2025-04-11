Ext._define('raf.specialorgan.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'raf.specialorgan.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = new Ext.grid.ColumnModel({
                columns: [
                    {
                      header: 'Orgão',
                      dataIndex: 'location_unicode',
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
    'raf.specialorgan.Restful',
    'raf.specialorgan.Grid'
);
