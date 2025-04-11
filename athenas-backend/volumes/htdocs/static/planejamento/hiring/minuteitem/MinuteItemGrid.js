Ext._define('planning.hiring.minuteitem.MinuteItemGrid', {
    extend: 'core.RestfulGrid',

    rest: 'planning.hiring.minuteitem.MinuteItemRestful',
    restWindow: 'planning.hiring.minuteitem.MinuteItemWindow',

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'disable', '-', 'search', 'import'],

    getColumnModel: function () {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    { header: 'ATA', dataIndex: 'minute_unicode', hidden: true },
                    { header: 'Grupo/Item', dataIndex: 'group', width: 80, sortable: true },
                    { header: 'Linha', dataIndex: 'line', width: 65, sortable: true },
                    { header: 'Descrição', dataIndex: 'description_without_tags', id: 'autoExpandColumn' },
                    { header: 'Unid. de Medida', dataIndex: 'unit_measure_display', hidden: true },
                    { header: 'Quantidade', dataIndex: 'quantity', width: 70, align: 'center' },
                    { header: 'Valor Unitário', dataIndex: 'unitary_value', width: 80, 'renderer': toolkit.util.formatCurrency },
                    { header: 'Valor Total', dataIndex: 'total_value', width: 80, 'renderer': toolkit.util.formatCurrency },
                    { header: 'Criado por', dataIndex: 'created_by_unicode', width: 120, hidden: true },
                    { header: 'Criado em', dataIndex: 'created_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), hidden: true },
                    { header: 'Modificado por', dataIndex: 'modified_by_unicode', width: 120, hidden: true },
                    { header: 'Modificado em', dataIndex: 'modified_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), hidden: true },
                ]
            );

        return this._columnModel;
    },

    createItem: function (values) {
        this.setParam('minute', this.params.minute);
        planning.hiring.minuteitem.MinuteItemGrid.superclass.createItem.call(this, values);
    },

    createGroup: function (values) {

        Ext._create('planning.hiring.minuteitem.MinuteItemGroupWindow', {
            action: 'create',
            values: values,
            params: this.getParams(),
            ownerGrid: this,
            callback: {
                success: {
                    scope: this,
                    fn: function (instance) {
                        if (this.driver === 'restful') this.getStore().reload();
                        this.fireEvent('createdItemGrid', instance);
                    }
                },
                failure: {
                    scope: this,
                    fn: function () {
                        if (this.driver === 'restful') this.getStore().reload();
                        this.fireEvent('failureGrid', 'create');
                    }
                }
            }
        }).show();
    },

    updateGroup: function (record) {
        var selections = core.nullValue(record, this.getSelectionModel().getSelections());
        if (selections.length == 1) {
            var selected = selections[0];
            Ext._create('planning.hiring.minuteitem.MinuteItemGroupWindow', {
                action: 'update',
                oId: selected.get('pk'),
                values: selected.data,
                params: this.getParams(),
                ownerGrid: this,
                callback: {
                    success: {
                        scope: this,
                        fn: function (instance) {
                            if (this.driver === 'restful') this.getStore().reload();
                            this.fireEvent('updatedItemGrid', instance);
                        }
                    },
                    failure: {
                        scope: this,
                        fn: function () {
                            if (this.driver === 'restful') this.getStore().reload();
                            this.fireEvent('failureGrid', 'update');
                        }
                    }
                }
            }).show();
        } else {
            Ext.Msg.show({
                title: 'Editando',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Selecione apenas um item para edição.'
            });
        }
    },

    doubleClick: function (grid) {
        var selected = this.getSelectionModel().getSelected();
        if (selected) {
            if (selected.get("unitary_value") == null || selected.get("quantity") == null)
                this.updateGroup();
            else
                this.updateItem();
        }
    },

    execMinuteItemAction: function (num) {
        var selected = this.getSelectionModel().getSelected();
        if (selected) {
            var wnd = Ext._create('planning.hiring.minuteitem.MinuteItemActionWindow', {
                params: {
                    action: num,
                    item: selected.get('pk'),
                    user: 845,
                },
                callback: {
                    success: {
                        scope: this,
                        fn: function (args) {
                            this.getStore().reload();
                        }
                    }
                },
                action: 'create',
            });

            wnd.show();
        } else {
            Ext.Msg.show({
                title: 'Atenção',
                icon: Ext.Msg.INFO,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione uma item para desativar.'
            });
        }
    },

    getDisableAction: function () {
        if (!this._disableAction)
            this._disableAction = Ext._create('Ext.Button', {
                text: 'Desativar Item',
                iconCls: 'icon-agree icon-agree-delete',
                scope: this,
                handler: function () {
                    this.execMinuteItemAction(2);
                }
            });

        return this._disableAction;
    },

    getImportAction: function () {
        if (!this._importAction) {
            this._importAction = Ext._create('Ext.Button', {
                text: 'Importar Itens',
                icon: "/" + global.Context + "/static/images/upload.png",
                scope: this,
                handler: function () {
                    Ext._create('planning.hiring.minuteitem.MinuteItemUploadFileWindow', {
                        params: this.params,
                        gridItems: this
                    }).show();
                }
            });
        }

        return this._importAction;
    },

    getToolbar: function (cfg) {
        var newComponent;

        if (!this._toolbar) {
            cfg = core.nullValue(cfg, {});

            this._toolbar = planning.hiring.minuteitem.MinuteItemGrid.superclass.getToolbar.call(this, cfg);
            this._toolbar.findBy(
                function (item) {
                    if (item.text == 'Novo')
                        newComponent = item;

                }
            );
            this._toolbar.remove(newComponent);

            this._toolbar.insert(0,
                {
                    text: 'Grupo/Item Agrupado',
                    iconCls: true,
                    icon: "/" + global.Context + "/static/images/icons/add.png",
                    scope: this,
                    handler: function () {
                        this.createGroup();
                    },
                }
            );

            this._toolbar.insert(1,
                {
                    text: 'Item/Linha',
                    iconCls: true,
                    icon: "/" + global.Context + "/static/images/icons/add.png",
                    scope: this,
                    handler: function () {
                        this.createItem();
                    },
                }
            )
        }

        return this._toolbar;
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(cfg, {
            doubleClickHandler: this.doubleClick,
            viewConfig: {
                scope: this,
                getRowClass: function (record) {
                    if (record.get('status') == 2) {
                        return 'x-grid3-unabled';
                    }
                    if (record.get('unitary_value') == null && record.get('line') == "") {
                        return 'x-grid3-yellow-simple';
                    }
                }
            }
        });

        planning.hiring.minuteitem.MinuteItemGrid.superclass.constructor.call(this, cfg);
    }

});

core.RestfulGrid.register(
    'planning.hiring.minuteitem.MinuteItemRestful',
    'planning.hiring.minuteitem.MinuteItemGrid'
);
