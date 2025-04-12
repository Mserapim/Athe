Ext._define('corregedoria.prontuary.individualperformance.coursesparticipation.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.prontuary.individualperformance.coursesparticipation.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 30, renderer: core.rendererIconGrid, menuDisabled: true, },
                    {header: 'Curso', dataIndex: 'course', id: 'autoExpandColumn', },
                    {header: 'Nível', dataIndex: 'course_level_unicode', width: 150, },
                    // {header: 'Data', dataIndex: 'date_course', width: 100, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                    {header: 'Pontuação', dataIndex: 'score', width: 90, },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.prontuary.individualperformance.coursesparticipation.Restful',
    'corregedoria.prontuary.individualperformance.coursesparticipation.Grid'
);
