Ext._define('corregedoria.inspection.inspection.filling.structure.personalmovement.ExternalPeoplesGrid', {
    extend: 'corregedoria.inspection.inspection.filling.structure.personalmovement.BaseGrid',

    rest: 'corregedoria.inspection.inspection.filling.structure.personalmovement.ExternalPeoplesRestful',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = new Ext.grid.ColumnModel({
                columns: [
                    { header: 'Servidor', dataIndex: 'employee_unicode', width: 400, sortable: false, menuDisabled: true, },
                    { header: 'Categoria', dataIndex: 'category', width: 400, sortable: false, menuDisabled: true, },
                    { header: 'Cargo/Função', dataIndex: 'occupation_unicode', id: 'autoExpandColumn', sortable: false, menuDisabled: true, },
                ],
            });
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.inspection.inspection.filling.structure.personalmovement.ExternalPeoplesRestful',
    'corregedoria.inspection.inspection.filling.structure.personalmovement.ExternalPeoplesGrid'
);
