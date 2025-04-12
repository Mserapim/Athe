Ext._define('corregedoria.inspection.inspection.filling.regularityofservices.processesforanalysisperformanceinaudiences.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.inspection.inspection.filling.regularityofservices.processesforanalysisperformanceinaudiences.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Tipo de Ação', dataIndex: 'action_type_title', width: 250, },
                    {header: 'Número do Feito', dataIndex: 'action_number', width: 170, },
                    {header: 'Tipo de Audiência', dataIndex: 'audience_type_display', id: 'autoExpandColumn', },
                    {header: 'Intimação', dataIndex: 'intimation', width: 70, renderer: toolkit.util.formatIconYesNo, align: 'center'},
                    {header: 'Presença', dataIndex: 'presence', width: 70, renderer: toolkit.util.formatIconYesNo, align: 'center'},
                    {header: 'Reperguntas', dataIndex: 'questions', width: 80, renderer: toolkit.util.formatIconYesNo, align: 'center'},
                    {header: 'Manifestação Oral', dataIndex: 'oral_manifestation', width: 115, renderer: toolkit.util.formatIconYesNo, align: 'center'},
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.inspection.inspection.filling.regularityofservices.processesforanalysisperformanceinaudiences.Restful',
    'corregedoria.inspection.inspection.filling.regularityofservices.processesforanalysisperformanceinaudiences.Grid'
);
