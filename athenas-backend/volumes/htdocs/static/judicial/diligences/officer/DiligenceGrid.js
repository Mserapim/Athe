Ext._define('judicial.diligences.officer.DiligenceGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'judicial.diligences.officer.DiligenceWindow',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons_status', width: 25, renderer: core.rendererIconGrid, menuDisabled: true},
                    {header: 'Descricao', dataIndex: 'unicode', id: 'autoExpandColumn'},
                    {header: 'Comarca', dataIndex: 'work_county_unicode', width: 150},
                    {header: 'Pontuação', dataIndex: 'score', width: 80, hidden: true},
                    {header: 'Situação', dataIndex: 'status_display', width: 80, hidden: false},
                    {header: 'Afastado?', dataIndex: 'is_removed_display', width: 80}
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'judicial.diligences.officer.DiligenceRestful',
    'judicial.diligences.officer.DiligenceGrid'
);
