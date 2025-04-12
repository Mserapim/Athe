Ext._define('corregedoria.inspection.inspection.filling.administrativeorganization.archivedprocedures.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.inspection.inspection.filling.administrativeorganization.archivedprocedures.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Número', dataIndex: 'number', width: 100, },
                    {header: 'Data de Instauração', dataIndex: 'instauration_date', renderer: Ext.util.Format.dateRenderer('d/m/Y'), width: 125, },
                    {header: 'Data de Arquivamento', dataIndex: 'archived_date', renderer: Ext.util.Format.dateRenderer('d/m/Y'), width: 125, },
                    {header: 'Tipo', dataIndex: 'taxonomy_class_title', width: 300, },
                    {header: 'Assunto', dataIndex: 'taxonomy_matter_title', id: 'autoExpandColumn', },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.inspection.inspection.filling.administrativeorganization.archivedprocedures.Restful',
    'corregedoria.inspection.inspection.filling.administrativeorganization.archivedprocedures.Grid'
);
