Ext._define('corregedoria.prontuary.functionalperformance.inspectionlink.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.prontuary.functionalperformance.inspectionlink.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'active', width: 30, renderer: toolkit.util.formatIconYesNo, },
                    {header: 'Órgão de Execução', dataIndex: 'inspection_execution_organ', id: 'autoExpandColumn', },
                    {header: 'Data de Início', dataIndex: 'inspection_date_initial', width: 100, },
                    {header: 'Data de Término', dataIndex: 'inspection_date_final', width: 100, },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.prontuary.functionalperformance.inspectionlink.Restful',
    'corregedoria.prontuary.functionalperformance.inspectionlink.Grid'
);
