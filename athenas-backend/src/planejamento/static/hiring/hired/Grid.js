Ext._define('planning.hiring.hired.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'planning.hiring.hired.Window',

    getColumnModel: function() {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel', [
                    Ext._create('Ext.grid.RowNumberer'),
                    { header: 'Pessoa', dataIndex: 'person_unicode', sortable: true, id: 'autoExpandColumn' },
                    { header: 'Data Início', dataIndex: 'start_date', sortable: true, menuDisabled: true, width: 70 },
                    { header: 'Data de Encerramento', dataIndex: 'end_date', sortable: true, width: 70 },
                ]
            );

        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        Ext.applyIf(cfg, {
            columnAction: false,
        });

        planning.hiring.hired.Grid.superclass.constructor.call(this, cfg);
    }
});

core.RestfulGrid.register(
    'planning.hiring.hired.Restful',
    'planning.hiring.hired.Grid'
);