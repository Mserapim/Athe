Ext._define('planning.hiring.corporatestructure.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'planning.hiring.corporatestructure.Window',

    getColumnModel: function() {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel', [
                    Ext._create('Ext.grid.RowNumberer'),
                    { header: 'Pessoa', dataIndex: 'person_unicode', sortable: true, width: 400 },
                    { header: 'Cargo', dataIndex: 'office_unicode', sortable: true, id: 'autoExpandColumn' },
                    { header: 'Data Inicial', dataIndex: 'start_date', sortable: true, menuDisabled: true, width: 100 },
                    { header: 'Data Desligamento', dataIndex: 'end_date', sortable: true, menuDisabled: true, width: 120 },
                ]
            );

        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        Ext.applyIf(cfg, {
            columnAction: false,
        });

        planning.hiring.corporatestructure.Grid.superclass.constructor.call(this, cfg);
    }
});

core.RestfulGrid.register(
    'planning.hiring.corporatestructure.Restful',
    'planning.hiring.corporatestructure.Grid'
);