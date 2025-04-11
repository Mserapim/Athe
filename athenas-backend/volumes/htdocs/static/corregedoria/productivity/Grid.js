Ext._define('corregedoria.productivity.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.productivity.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Produtividade', dataIndex: 'productivity_display', width: 85, },
                    {header: 'Tabela de Pontuação', dataIndex: 'score_table_display', id: 'autoExpandColumn', },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.productivity.Restful',
    'corregedoria.productivity.Grid'
);
