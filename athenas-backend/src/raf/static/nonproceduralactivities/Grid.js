Ext._define('raf.nonproceduralactivities.Grid', {
    extend: 'core.RestfulGrid',
    restWindow: 'raf.nonproceduralactivities.Window',
    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Data', dataIndex: 'date', renderer: Ext.util.Format.dateRenderer('d/m/Y'), width: 70},
                    {header: 'Procedimento Legal', dataIndex: 'legal_procedure_unicode', width: 450},
                    {header: 'Título', dataIndex: 'title', width: 500},
                    {header: 'Descrição', dataIndex: 'description', id: 'autoExpandColumn'},
                ]
            );
        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                columnAction: false
            }
        );
        raf.nonproceduralactivities.Grid.superclass.constructor.call(this, cfg);
    }
});
core.RestfulGrid.register(
    'raf.nonproceduralactivities.Restful',
    'raf.nonproceduralactivities.Grid'
);
