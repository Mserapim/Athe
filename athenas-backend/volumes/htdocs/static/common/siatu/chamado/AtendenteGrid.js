/**
 *
 **/
Ext._define('common.siatu.chamado.AtendenteGrid', {
    extend: 'common.siatu.chamado.Grid',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Codigo', dataIndex: 'identificacao', width: 80, sortable:true},
                    {header: 'Status', dataIndex: 'icon_status', width: 130, renderer: common.siatu.rendererIconGrid},
                    {header: 'Tempo decorrido', dataIndex: 'tempo_decorrido', width: 100},
                    // {header: 'Fila', dataIndex: 'fila', width: 32, sortable:true, renderer: function(value){return (value == 0) ? '' : value} },
                    // {header: 'Fila tipo', dataIndex: 'tipo_fila', width: 125, sortable:false, renderer: function(value){return (value == 0) ? '' : value} },
                    {header: 'Solicitante', dataIndex: 'solicitante_username', width: 100, sortable:true},
                    {header: 'Serviço', dataIndex: 'servico_unicode', width: 150, sortable:true, id: 'autoExpandColumn',},
                    // {header: 'Problema', dataIndex: 'problema_solicitante', id: 'autoExpandColumn', sortable:true, hidden:true},
                    // {header: 'Motivo Urgência', dataIndex: 'motivo_urgencia', width: 140, sortable:true},
                    // {header: 'Chamado anterior', dataIndex: 'chamado_anterior', width: 100, hidden: true},

                ]
            );

        return this._columnModel;
    },

});
