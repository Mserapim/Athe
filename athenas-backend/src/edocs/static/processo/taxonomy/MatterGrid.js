Ext._define('edocs.processo.taxonomy.MatterGrid', {
    extend: 'core.RestfulGrid',
    restWindow: 'edocs.processo.taxonomy.MatterWindow',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 26, renderer: core.rendererIconGrid, menuDisabled: true},
                    {header: 'Assunto', dataIndex: 'legal_matter_unicode', id: 'autoExpandColumn'},
                    {header: 'Principal', dataIndex: 'principal', hidden: true, truewidth: 130},
                    {header: 'Processo', dataIndex: 'process_unicode', hidden: true, truewidth: 130},
                ]
            );

        return this._columnModel;
    }

});

core.RestfulGrid.register(
    'edocs.processo.taxonomy.MatterRestful',
    'edocs.processo.taxonomy.MatterGrid'
);
