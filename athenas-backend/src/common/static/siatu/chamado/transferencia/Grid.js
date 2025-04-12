/**
 *
 **/
Ext._define('common.siatu.chamado.transferencia.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'common.siatu.chamado.transferencia.Window',

    keywordFieldMessage: '',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Data pedido', dataIndex: 'data_pedido', width: 110},
                    {header: 'Pedido por', dataIndex: 'pedido_por', width:110},
                    {header: 'Aceito por', dataIndex: 'aceito_por', width:110},
                    {header: 'Data aceite', dataIndex: 'data_aceite', width: 110},
                    {header: 'Motivo', dataIndex: 'motivo', id: 'autoExpandColumn'},
                    {header: 'Cancelado', dataIndex: 'cancelado', width: 90, renderer: function(value) { return value ? 'Sim' : '' }},
                ]
            );

        return this._columnModel;
    },

    createItem: function(values) {
        values = core.nullValue(values, {});

        this.factoryRestfulWindow({
            action: 'create',
            params: this.getParams(),
            values: values,
            super_user: this.super_user,
            callback: this.callback
        }).show();
    },

    getToolbar: function(cfg) {
        if(!this._toolbar) {
            this._toolbar = Ext._create('Ext.Toolbar', {
                style: cfg.toolbarStyle,
                items: [
                    {
                        text: 'Novo',
                        iconCls: 'icon-core icon-core-add',
                        scope: this,
                        handler: this.createItem
                    },
                    '-',
                    'Buscar por :',
                    ' ',
                    this.getKeywordField(),
                    '-',
                    '->'
                ]
            });

            var filterMenu = this.getFilterMenu();
            if(filterMenu)
                this._toolbar.add([
                    '-',
                    {
                        text: 'Filtro',
                        iconCls: 'icon-patrimonio icon-pat-filter',
                        menu: filterMenu
                    }
                ]);
        }

        return this._toolbar;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                super_user: false,
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getStore().reload();
                        }
                    }
                }
            }
            );

        Ext.apply(
            cfg,
            {
                columnAction: false,
                allowRemove: false,
                allowUpdate: false,
            }
        );

        this.super_user=cfg.super_user;
        common.siatu.chamado.transferencia.Grid.superclass.constructor.call(this, cfg);
    }

})
