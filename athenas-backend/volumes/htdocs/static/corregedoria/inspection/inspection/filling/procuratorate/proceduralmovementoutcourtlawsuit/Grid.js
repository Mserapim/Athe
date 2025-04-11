Ext._define('corregedoria.inspection.inspection.filling.procuratorate.proceduralmovementoutcourtlawsuit.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.inspection.inspection.filling.procuratorate.proceduralmovementoutcourtlawsuit.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Ano', dataIndex: 'year', width: 65, align: 'center'},
                    {header: 'Janeiro', dataIndex: 'amount_january', width: 75, align: 'center'},
                    {header: 'Fevereiro', dataIndex: 'amount_february', width: 75, align: 'center'},
                    {header: 'Março', dataIndex: 'amount_march', width: 75, align: 'center'},
                    {header: 'Abril', dataIndex: 'amount_april', width: 75, align: 'center'},
                    {header: 'Maio', dataIndex: 'amount_may', width: 75, align: 'center'},
                    {header: 'Junho', dataIndex: 'amount_june', width: 75, align: 'center'},
                    {header: 'Julho', dataIndex: 'amount_july', width: 75, align: 'center'},
                    {header: 'Agosto', dataIndex: 'amount_august', width: 75, align: 'center'},
                    {header: 'Setembro', dataIndex: 'amount_september', width: 75, align: 'center'},
                    {header: 'Outubro', dataIndex: 'amount_october', width: 75, align: 'center'},
                    {header: 'Novembro', dataIndex: 'amount_november', width: 75, align: 'center'},
                    {header: 'Dezembro', dataIndex: 'amount_december', width: 75,  align: 'center'},
                    {header: 'Total', dataIndex: 'sum_amount', id: 'autoExpandColumn', align: 'center'},
                ]
            );

        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.inspection.inspection.filling.procuratorate.proceduralmovementoutcourtlawsuit.Restful',
    'corregedoria.inspection.inspection.filling.procuratorate.proceduralmovementoutcourtlawsuit.Grid'
);
