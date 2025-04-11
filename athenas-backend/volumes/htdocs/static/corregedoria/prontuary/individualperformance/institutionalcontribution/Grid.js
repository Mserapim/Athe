Ext._define('corregedoria.prontuary.individualperformance.institutionalcontribution.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.prontuary.individualperformance.institutionalcontribution.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    // {header: '', dataIndex: 'icons', width: 30, renderer: core.rendererIconGrid, menuDisabled: true, },
                    {header: 'Contribuição', dataIndex: 'contribution', id: 'autoExpandColumn', },
                    // {header: 'Data', dataIndex: 'date_edital', width: 100, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.prontuary.individualperformance.institutionalcontribution.Restful',
    'corregedoria.prontuary.individualperformance.institutionalcontribution.Grid'
);
