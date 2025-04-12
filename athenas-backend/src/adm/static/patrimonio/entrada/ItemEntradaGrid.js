/**
 *
 **/
Ext._define('adm.patrimonio.entrada.ItemEntradaGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'adm.patrimonio.entrada.ItemEntradaWindow',

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'suspension', '-', 'search', '->', 'download'],

    openSuspensionWindow: function() {
        var selected = this.getSelectionModel().getSelected();

        if(selected) {
            var grid = Ext._create('adm.patrimonio.SuspensaoGrid');

            grid.setFilterProperty('nota_entrada', selected.get('nota'), 100, false);
            grid.setFilterProperty('item_entrada', selected.get('pk'), 101, false);

            grid.setParam('nota_entrada', selected.get('nota'));
            grid.setParam('item_entrada', selected.get('pk'));

            var wnd = Ext._create('Ext.Window', {
                title: 'Suspensão de Entrada',
                modal: true,
                border: false,
                width: 750,
                height: 450,
                layout: 'fit',
                items: [grid]
            });

            wnd.show();
        }
        else
            Ext.Msg.show({
                title: 'Suspensão de entrada',
                msg: 'Primeiro selecione um item para ser suspenso.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    getSuspensionAction: function(cfg) {
        if(!this._suspensionAction)
            this._suspensionAction = Ext._create('Ext.Button', {
                text: 'Suspensão',
                scope: this,
                iconCls: 'icon-patrimonio icon-pat-cancelado',
                handler: this.openSuspensionWindow
            });

        return this._suspensionAction;
    },

    getStore: function(cfg) {
        if(!this._store) {
            this._store = adm.patrimonio.entrada.ItemEntradaGrid.superclass.getStore.call(this, cfg);
            this._store.on({
                scope: this,
                load: function() {
                    this.balance = 0;
                }
            });
        }

        return this._store;
    },

    formatBalance: function(value) {
        this.balance = (this.balance || 0) + value;
        return '<div style="text-align:right">' + Ext.util.Format.number(this.balance, '0.000,00/i') + '</div>';
    },

    getColumnModel: function() {
        var me = this;

        if(!this._columnModel) {
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
                    {header: 'Especie', dataIndex: 'especie_unicode', id: 'autoExpandColumn'},
                    {header: 'Conservação', dataIndex: 'conservacao_display', width: 105},
                    {
                        header: 'Garantia',
                        dataIndex: 'meses_garantia',
                        width: 85,
                        renderer: function(value) {return value + ' mes(es)';}
                    },
                    {
                        header: 'Qnt.',
                        dataIndex: 'quantidade',
                        width: 65,
                        renderer: function(value) {return '<div style="text-align:right">' + value + '</div>';}
                    },
                    {
                        header: 'Unitário',
                        dataIndex: 'valor_unitario',
                        width: 65,
                        renderer: toolkit.util.formatCurrency
                    },
                    {
                        header: 'Total',
                        dataIndex: 'valor_total',
                        width: 95,
                        renderer: toolkit.util.formatCurrency
                    },
                    {
                        header: 'Acumulado',
                        dataIndex: 'valor_total',
                        width: 95,
                        renderer: function(value) { return me.formatBalance(value); }
                    }
                ]
            );
        }

        return this._columnModel;
    },
});
