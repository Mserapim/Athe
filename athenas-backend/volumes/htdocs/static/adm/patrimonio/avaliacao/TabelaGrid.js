/**
 *
 **/
Ext._define('adm.patrimonio.avaliacao.TabelaGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'adm.patrimonio.avaliacao.TabelaWindow',

    getToolbar: function(cfg) {
        if(!this._toolbar) {
            this._toolbar = adm.patrimonio.avaliacao.TabelaGrid.superclass.getToolbar.call(this, cfg);

            this._toolbar.insert(3, {
                text: 'Copiar',
                scope: this,
                handler: this.openCopyWindow
            });
            this._toolbar.insert(3, '-');
        }

        return this._toolbar;
    },

    openCopyWindow: function() {
        Ext._create('adm.patrimonio.avaliacao.TabelaCopyWindow', {
            modal: true,
            values: {
                src: 0,
                dst: 0
            },
            callback: {
                success: {
                    scope: this,
                    fn: function() { this.getStore().reload(); }
                }
            }
        }).show();
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {
                        header: 'Numero',
                        dataIndex: 'numero_formatado',
                        width: 70,
                        menuDisabled: true,
                    },
                    {
                        header: 'Publicação',
                        dataIndex: 'publicacao_unicode',
                        id: 'autoExpandColumn'
                    },
                    {
                        header: 'Vigencia',
                        dataIndex: 'data_vigencia',
                        width: 70,
                        renderer: Ext.util.Format.dateRenderer('d/m/Y')
                    },
                    {
                        header: 'Fim',
                        dataIndex: 'data_fim_vigencia',
                        width: 70,
                        renderer: Ext.util.Format.dateRenderer('d/m/Y')
                    }
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'adm.patrimonio.avaliacao.TabelaRestful',
    'adm.patrimonio.avaliacao.TabelaGrid'
);
