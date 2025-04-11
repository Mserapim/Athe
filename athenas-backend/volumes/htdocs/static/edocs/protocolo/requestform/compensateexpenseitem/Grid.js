Ext._define('edocs.protocolo.requestform.compensateexpenseitem.Grid', {
    extend: 'core.RestfulGrid',
    restWindow: 'edocs.protocolo.requestform.compensateexpenseitem.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Cod', dataIndex: 'pk', width: 50, hidden: true},
                    {header: 'Ressarcimento', dataIndex: 'compensate_item_unicode', width: 120, hidden: true},
                    {header: 'Número da nota fiscal', dataIndex: 'nota', id: 'autoExpandColumn', width: 180},
                    {header: 'Nome da empresa ou do prestador de serviço', dataIndex: 'company', id: 'autoExpandColumn', width: 180},
                    {header: 'Data de vencimento', dataIndex: 'venc_date_nf', id: 'autoExpandColumn', width: 100,  renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                    {header: 'Nota de material', dataIndex: 'nota_material', id: 'autoExpandColumn', width: 100, renderer: function(value) { return (value ? 'SIM' : 'NÃO'); }},
                    {header: 'Nota de serviço', dataIndex: 'nota_service', id: 'autoExpandColumn', width: 100, renderer: function(value) { return (value ? 'SIM' : 'NÃO'); }},
                    {header: 'Valor', dataIndex: 'value', id: 'autoExpandColumn', width: 75, renderer: toolkit.util.formatCurrency},
                    // {header: 'Por', dataIndex: 'modified_by_unicode', width: 190},
                    // {header: 'Quando', dataIndex: 'modified_at', width: 100, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.compensateexpenseitem.Restful',
    'edocs.protocolo.requestform.compensateexpenseitem.Grid'
);
