Ext._define('corregedoria.inspection.inspection.filling.structure.personalmovement.BaseGrid', {
    extend: 'rh.movimentacao.pessoal.Grid',

    rest: 'corregedoria.inspection.inspection.filling.structure.personalmovement.BaseRestful',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = new Ext.grid.ColumnModel({
                columns: [
                    { header: 'Servidor', dataIndex: 'employee_unicode', width: 450, sortable: false, menuDisabled: true, },
                    { header: 'Cargo/Função', dataIndex: 'occupation_unicode', id: 'autoExpandColumn', sortable: false, menuDisabled: true, },
                ],
            });
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.inspection.inspection.filling.structure.personalmovement.BaseRestful',
    'corregedoria.inspection.inspection.filling.structure.personalmovement.BaseGrid'
);
