Ext._define('planning.hiring.enterprise.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'planning.hiring.enterprise.Window',

    getColumnModel: function() {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel', [
                    Ext._create('Ext.grid.RowNumberer'),
                    { header: 'Empresa', dataIndex: 'person_unicode', sortable: true, id: 'autoExpandColumn' },
                    { header: 'Não se aplica?', dataIndex: 'apply', sortable: true, width: 100, renderer: toolkit.util.formatIconYesNo },
                    { header: 'Motivo', dataIndex: 'motive_unicode', sortable: true, width: 200 }
                ]
            );

        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        Ext.applyIf(cfg, {
            columnAction: false,
        });

        planning.hiring.enterprise.Grid.superclass.constructor.call(this, cfg);
    }
});

core.RestfulGrid.register(
    'planning.hiring.enterprise.Restful',
    'planning.hiring.enterprise.Grid'
);