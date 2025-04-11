Ext._define('rh.pvf.portalusufructretification.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.pvf.portalusufructretification.Window',

    getColumnModel: function () {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    { header: 'Cod', dataIndex: 'pk', width: 50, hidden: true },
                    { header: 'descricao', dataIndex: 'status_display', id: 'autoExpandColumn' },
                    { header: 'Situação', dataIndex: 'status_type', width: 140},
                    { header: 'Programação', dataIndex: 'subtype_usufruct', width: 140},
                    { header: 'Início', dataIndex: 'start_date', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y') },
                    { header: 'Fim', dataIndex: 'end_date', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y') },
                    { header: 'Dias programados/Vendidos', dataIndex: 'days', width: 100 },
                    { header: 'Tipo', dataIndex: 'type_activity', width: 90},
                    { header: 'Início do período aquisitivo', dataIndex: 'start_date_acquisition', width: 120, renderer: Ext.util.Format.dateRenderer('d/m/Y') },


                ]
            );

        return this._columnModel;
    }

});


core.RestfulGrid.register(
    'rh.pvf.portalusufructretification.Restful',
    'rh.pvf.portalusufructretification.Grid'
);    