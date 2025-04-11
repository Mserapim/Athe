Ext._define('common.saci.step.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'common.saci.step.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'unicode', id: 'autoExpandColumn', hidden: true},
                    {header:'De', dataIndex: 'origin_unicode', width:350, hidden:false},
                    {header:'Para', dataIndex: 'destination_unicode', width:350, hidden:false},
                    {header:'Encaminhado em', dataIndex: 'created_at', width:100, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), hidden:false},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'common.saci.step.Restful',
    'common.saci.step.Grid'
);
