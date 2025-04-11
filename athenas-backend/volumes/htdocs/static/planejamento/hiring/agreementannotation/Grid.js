Ext._define('planning.hiring.agreementannotation.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'planning.hiring.agreementannotation.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Tipo', dataIndex: 'kind_display', width: 90},
                    {header: 'Contrato', dataIndex: 'agreement_unicode', width: 150, hidden: true},
                    {header: 'Nota', dataIndex: 'note', id: 'autoExpandColumn' },
                    {header: 'Data', dataIndex: 'date', width: 90},
                    {header: 'Data Agendada?', dataIndex: 'schedule', width: 75, hidden: false, renderer: function (value) { return (value ? 'Sim' : 'Não'); }},
                    {header: 'Data Agendamento', dataIndex: 'schedule_date', width: 90}
                ]
            );

        return this._columnModel;
    },

     constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        planning.hiring.agreementannotation.Grid.superclass.constructor.call(this, cfg);
    },
});

core.RestfulGrid.register(
    'planning.hiring.agreementannotation.Restful',
    'planning.hiring.agreementannotation.Grid'
);