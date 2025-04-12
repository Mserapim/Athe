Ext._define('rh.nomeacao.anexo_nomeacao.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.nomeacao.anexo_nomeacao.Window',

    configOrderToolBar: [
        'search',
    ],

    hideActions: ['add', 'edit', 'copy', 'remove', 'download'],

    getColumnModel: function(cfg) {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Chave', dataIndex: 'pk', id: 'autoExpandColumn', hidden: true},
                    {header: 'Tipo Documento', dataIndex: 'tipo_documento_display', width: 300},

                ]
            );

        return this._columnModel;
    },    

    getConfigCustomActions: function(){
        return [
            {
                iconCls: 'icon-16px icon-fopag icon-compile',
                tooltip: 'Download',
                scope: this,
                handler: function(action, index){
                    var anexo = action._store.getAt(index).data
                    params = { 'anexo_pk': anexo.pk };

                    this.reqDownload('RHNomeacaoAnexoRestful', 'download_anexo', params, 'documento.pdf');
                },
            },
        ];
    },

});

core.RestfulGrid.register(
    'rh.nomeacao.anexo_nomeacao.Restful',
    'rh.nomeacao.anexo_nomeacao.Grid'
);