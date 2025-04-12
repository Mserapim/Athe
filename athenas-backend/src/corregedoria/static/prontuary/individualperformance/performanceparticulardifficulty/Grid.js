Ext._define('corregedoria.prontuary.individualperformance.performanceparticulardifficulty.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.prontuary.individualperformance.performanceparticulardifficulty.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 30, renderer: core.rendererIconGrid, menuDisabled: true, },
                    {header: 'Atuação em', dataIndex: 'employeelocation_description', id: 'autoExpandColumn', },
                    {header: 'Dias', dataIndex: 'total_days', width: 90, },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.prontuary.individualperformance.performanceparticulardifficulty.Restful',
    'corregedoria.prontuary.individualperformance.performanceparticulardifficulty.Grid'
);
