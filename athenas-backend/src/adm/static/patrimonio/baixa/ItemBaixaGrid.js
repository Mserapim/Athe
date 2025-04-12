Ext._define('adm.patrimonio.baixa.ItembaixaGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'adm.patrimonio.baixa.ItemBaixaWindow',

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'importItems', '-', 'search', '->', 'download'],

    getImportItemsAction: function(cfg) {
        if(!this._importItemsAction)
            this._importItemsAction = Ext._create('Ext.Button', {
                text: 'Importar',
                scope: this,
                handler: function() {
                    this.importFromInputNote();
                }
            });

        return this._importItemsAction;
    },

    __importFromInputNotes: function(pkset) {
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Importando ...'});

        mask.show();
        rest.importFromInputNotes(
            {
                nota: this.getParams().nota,
                pkset: pkset
            },
            {
                scope: this,
                fn: function() { this.getStore().reload(); }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Importando itens da Nota',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function() { mask.hide(); }
            }
        );
    },

    importFromInputNote: function() {
        var wnd = Ext._create('core.GridSelectWindow', {
            restGrid: 'adm.patrimonio.entrada.Grid',
            width: (screen.width * 0.9),
            height: (screen.height * 0.8),
            title: 'Selecione um Nota de entrada para importar patrimonios',
            multi: true,
            callback: {
                scope: this,
                fn: function(selection) {
                    this.__importFromInputNotes(selection.map(function(data) { return data.get('pk'); }));
                }
            }
        });

        wnd.getGridPanel().setFilterProperty('state', 2, 100, false);
        wnd.show();
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {
                        header: '',
                        dataIndex: 'icons',
                        width: 90,
                        menuDisabled: true,
                        renderer: adm.daily.rendererIconGrid
                    },
                    {header: 'Descrição', dataIndex: 'patrimonio_unicode', id: 'autoExpandColumn'},
                    {header: 'Conservação', dataIndex: 'conservacao', width: 105},
                    {
                        header: 'Tombo',
                        dataIndex: 'data_tombo',
                        width: 95,
                        renderer: Ext.util.Format.dateRenderer('d/m/Y')
                    },
                    {
                        header: 'Valor Atual',
                        dataIndex: 'valor_atual',
                        width: 85,
                        renderer: toolkit.util.formatCurrency
                    },
                    {
                        header: 'Valor Baixa',
                        dataIndex: 'valor_baixa',
                        width: 85,
                        renderer: toolkit.util.formatCurrency
                    },
                    {
                        header: 'Avaliação',
                        dataIndex: 'avaliacao',
                        width: 95,
                        renderer: toolkit.util.formatCurrency
                    }
                ]
            );

        return this._columnModel;
    },
});
