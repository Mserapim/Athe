Ext._define('planning.hiring.document.DocumentGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'planning.hiring.document.DocumentWindow',

    configOrderToolBar: ['add', 'edit', 'remove'],

    getColumnModel: function() {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel', [
                    Ext._create('Ext.grid.RowNumberer'),
                    { header: 'Nome', dataIndex: 'title', sortable: true, width: 200 },
                    { header: 'Arquivo', dataIndex: 'filename', sortable: true, menuDisabled: true, id: 'autoExpandColumn' },
                ]
            );

        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        Ext.applyIf(cfg, {
            columnAction: false,
        });

        planning.hiring.document.DocumentGrid.superclass.constructor.call(this, cfg);
    }
});

core.RestfulGrid.register(
    'planning.hiring.document.DocumentRestful',
    'planning.hiring.document.DocumentGrid'
);