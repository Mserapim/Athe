Ext._define('planning.hiring.minutesolicitationaction.MinuteSolicitationActionGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'planning.hiring.minutesolicitationaction.MinuteSolicitationActionWindow',

    configOrderToolBar: ['search',],

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Data', dataIndex: 'date'},
                    {header: 'Histórico', dataIndex: 'unicode', menuDisabled: true, width: 400},
                    {header: 'Observação', dataIndex: 'observation', id: 'autoExpandColumn'},
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

        planning.hiring.minutesolicitationaction.MinuteSolicitationActionGrid.superclass.constructor.call(this, cfg);
    },
});

core.RestfulGrid.register(
    'planning.hiring.minutesolicitationaction.MinuteSolicitationActionRestful',
    'planning.hiring.minutesolicitationaction.MinuteSolicitationActionGrid'
);