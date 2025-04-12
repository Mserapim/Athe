Ext._define('rh.pvf.person.Grid', {
    //extend: 'rh.person.naturalperson.Grid',
    extend: 'core.RestfulGrid',

    restWindow: 'rh.pvf.person.Window',

    columnAction: false,

    hideActions: ['edit','remove','copy'],
  
    hideItemsToolbar: ['edit', 'remove'],


    getColumnItems: function () {
        if (!this._items) {
            this._items = [
                Ext._create('Ext.grid.RowNumberer'),
                { header: 'Cod', dataIndex: 'pk', width: 50, hidden: true },
                { header: 'Nome', dataIndex: 'nome', id: 'autoExpandColumn', sortable: true },
                { header: 'Descricao', dataIndex: 'unicode', sortable: true, hidden: true },
            ];
        }

        return this._items;
    },

    getColumnModel: function () {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                this.getColumnItems()
            );
        return this._columnModel;
    }

});    

core.RestfulGrid.register(
    'rh.pvf.person.Restful',
    'rh.pvf.person.Grid'
);    