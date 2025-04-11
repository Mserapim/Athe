/**
 *
 **/
Ext._define('common.siatu.chamado.status.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'common.siatu.chamado.status.Window',

    keywordFieldMessage: '',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icon', width:25, renderer: common.siatu.rendererIconGrid},
                    {header: 'Status', dataIndex: 'status_display', width: 160},
                    {header: 'Data de início', dataIndex: 'data_inicio', width: 100},
                    {header: 'Previsão de fim', dataIndex: 'previsao_fim', width: 100},
                    {header: 'Terceirizada', dataIndex: 'terceirizada_string', width: 160},
                    {header: 'Observação', dataIndex: 'motivo', id: 'autoExpandColumn'},
                ]
            );

        return this._columnModel;
    },

    getActionColumn: function() {
        if(!this._actionColumn)
            this._actionColumn = Ext._create('Ext.grid.ActionColumn', {
                width: 65,
                scope: this,
                items: [
                    {
                        iconCls: 'icon-16px icon-core icon-core-edit',
                        tooltip: 'Editar item.',
                        handler: function(action, index) {
                            var record = this.getStore().getAt(index);
                            record && this.updateItem(record);
                        }
                    },
                ]
            });

        return this._actionColumn;
    },

    createItem: function(values) {
        if(!this.allowCreate)
            return;

        values = core.nullValue(values, {});

        this.factoryRestfulWindow({
            action: 'create',
            params: this.getParams(),
            values: values,
            callback: this.callback
        }).show();
    },

    updateItem: function(record) {
        if(!this.allowUpdate)
            return;

        if(record instanceof Ext.Button)
            record = undefined;

        var selected = core.nullValue(record, this.getSelectionModel().getSelected());
        // se Status for Aberto ou Aguardando Atendimento, então não pode editar
        if ( (selected.get('status') == 1) || (selected.get('status') == 2) ){
            console.debug('Não é possivel editar este status');
            return;
        }

        if(selected) {
            this.factoryRestfulWindow({
                action: 'update',
                oId: selected.get('pk'),
                values: selected.data,
                params: this.getParams(),
                callback: this.callback
            }).show();
        }
        else
            Ext.Msg.show({
                title: 'Editando',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item para editar.'
            });
    },

    removeItems: function(record) {
        if(!this.allowRemove)
            return;

        var selection;

        if(!(record instanceof Ext.Button))
            selection = [record];
        else
            selection = this.getSelectionModel().getSelections();

        var pk;
        var rest = this.factoryRestful();

        if(selection.length == 1) {
            pk = selection[0].get('pk');

            rest.remove(
                pk,
                {
                    externalCallback: this.callback
                },
                {
                    el: this.getEl(),
                    msg: 'Removendo item.'
                }
            );
        }
        else if(selection.length > 1) {
            pk = selection.map(function(selected) { return selected.get('pk'); });

            rest.remove(
                false,
                {
                    params: {
                        filter: Ext.encode([
                            {property: 'pk__in', value: pk}
                        ])
                    },
                    externalCallback: {
                        success: {
                            fn: function() { this.getStore().reload(); },
                            scope: this
                        }
                    }
                },
                {
                    el: this.getEl(),
                    msg: 'Removendo item.'
                }
            );
        }
        else
            Ext.Msg.show({
                title: 'Removendo',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Não foi selecionado nenhum item para remoção.'
            });
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
                    {
                        text: 'Editar',
                        iconCls: 'icon-core icon-core-edit',
                        scope: this,
                        handler: this.updateItem
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
        Ext.apply(cfg,{
            columnAction: false,
        });
        common.siatu.chamado.status.Grid.superclass.constructor.call(this, cfg);
    }

});
