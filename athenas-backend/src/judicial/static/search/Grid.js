Ext._define('judicial.search.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'judicial.search.Window',
    
    hideActions: ['add', 'edit', 'remove', 'download'],

    hideItemsToolbar: ['add', 'edit', 'remove', 'download'],

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {
                        menuDisabled: true,
                        id: 'autoExpandColumn',
                        dataIndex: '__ghost__',
                        header: 'Descrição',
                        renderer: this.__rendererItem
                    }
                ]
            );

        return this._columnModel;
    },

    __rendererItem: function (value, cell, data) {
        var tpl = new Ext.XTemplate(
            '<div class="edoc-row">',
                '<div class="edoc-iconset">',
                    core.rendererIconGrid(data.get('icons')),
                '</div>',
                '<div class="edoc-item">',
                    '<div>',
                        '<div class="subject inline-with-crop" ext:qtip="Assunto">{unicode}</div>',
                    '</div>',
                    '<div>',
                        '<div class="subject inline-with-crop" ext:qtip="Interessado">{lawsuit_unicode}</div>',
                    '</div>',
                    '<div class="two-column">',
                        '<tpl if="is_public">',
                            '<div class="one" ext:qtip="Situação">Documento público</div>',
                        '</tpl>',
                        '<tpl if="!is_public">',
                            '<div class="one" ext:qtip="Situação">Documento ainda não publicado</div>',
                        '</tpl>',
                        '<div class="two" ext:qtip="Data de assinatura">{signed_at:date("d/m/Y H:i")}</div>',
                    '</div>',
                    '<div class="two-column">',
                        '<div class="one" ext:qtip="Área de atuação">{lawsuit_location_unicode}</div>',
                        '<div class="two" ext:qtip="Assinado por por">{signed_by_unicode}</div>',
                    '</div>',
                '</div>',
            '</div>'
        );

        return tpl.apply(data.data);
    },

    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        Ext.applyIf(cfg, {
            columnAction: false,
            stripeRows: true,
            viewConfig: {
                deferEmptyText: false,
                emptyText: '<h1>Nenhum dado encontrado. Informe um termo para busca dos documentos.</h1>',
            },
        });

        judicial.search.Grid.superclass.constructor.call(this, cfg);
    }
});

core.RestfulGrid.register(
    'judicial.search.Restful',
    'judicial.search.Grid'
);

