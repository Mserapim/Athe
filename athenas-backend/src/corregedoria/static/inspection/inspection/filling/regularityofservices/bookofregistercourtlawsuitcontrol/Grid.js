Ext._define('corregedoria.inspection.inspection.filling.regularityofservices.bookofregistercourtlawsuitcontrol.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.inspection.inspection.filling.regularityofservices.bookofregistercourtlawsuitcontrol.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Livro', dataIndex: 'book', id: 'autoExpandColumn', },
                    {header: 'Data do Termo de Abertura', dataIndex: 'opening_date', renderer: Ext.util.Format.dateRenderer('d/m/Y'), width: 600, },
                ]
            );

        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.inspection.inspection.filling.regularityofservices.bookofregistercourtlawsuitcontrol.Restful',
    'corregedoria.inspection.inspection.filling.regularityofservices.bookofregistercourtlawsuitcontrol.Grid'
);
