Ext._define('planning.hiring.agreementaction.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'planning.hiring.agreementaction.Window',

    configOrderToolBar: ['search', '-',  '->'],

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Data', dataIndex: 'data_acao'},
                    {header: 'Histórico', dataIndex: 'unicode', menuDisabled: true, width: 400},
                    {header: 'Observação', dataIndex: 'observacao', id: 'autoExpandColumn'},
                ]
            );

        return this._columnModel;
    },

     constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        Ext.applyIf(cfg, {
            columnAction: false,
            allowCreate: false,
            allowUpdate: false,
            allowRemove: false,
        });

        planning.hiring.agreementaction.Grid.superclass.constructor.call(this, cfg);
    },
});

core.RestfulGrid.register(
    'planning.hiring.agreementaction.Restful',
    'planning.hiring.agreementaction.Grid'
);