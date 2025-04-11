/**
 *
 **/
Ext._define('edocs.processo.referencia.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'edocs.processo.referencia.Window',

    keywordFieldMessage: '',

    hideItemsToolbar: ['search', 'download', 'open'],

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Processo', dataIndex: 'referenciado_codigo', width: 160},
                    {header: 'Tipo', dataIndex: 'tipo_display', width: 100},
                    {header: 'Descrição', dataIndex: 'descricao', id: 'autoExpandColumn'},
                ]
            );

        return this._columnModel;
    },

    getConfigItemsToolbar: function(cfg) {
        hideItems = cfg.hideItemsToolbar || this.hideItemsToolbar;
        if(!this._configItemsToolbar) {
            this._configItemsToolbar = [];
            if(hideItems.indexOf('add') < 0) {
                this._configItemsToolbar.push(
                    {
                        text: 'Novo',
                        iconCls: 'icon-core icon-core-add',
                        scope: this,
                        handler: this.createItem,
                    }
                );
            }
            if(hideItems.indexOf('edit') < 0) {
                this._configItemsToolbar.push(
                    {
                        text: 'Editar',
                        iconCls: 'icon-core icon-core-edit',
                        scope: this,
                        handler: this.updateItem,
                    }
                );
            }
            if(hideItems.indexOf('remove') < 0) {
                this._configItemsToolbar.push(
                    {
                        text: 'Remover',
                        iconCls: 'icon-core icon-core-delete',
                        scope: this,
                        handler: this.removeItems,
                    }
                );
            }

            if(hideItems.indexOf('open') < 0) {
                this._configItemsToolbar.push(
                    {
                        text: 'Abrir Processo',
                        iconCls: true,
                        icon: "/" + global.Context + "/static/images/document-open.png",
                        scope: this,
                        handler: function() {
                            var selected = this.getSelectionModel().getSelected()
                            if (selected) {
                                this.openItemFunction()
                            }
                            else{
                                Ext.Msg.show({
                                   title: 'Visualização',
                                   icon: Ext.Msg.ERROR,
                                   buttons: Ext.Msg.OK,
                                   msg: 'Selecione um processo!'
                                });
                            }
                        }
                    }
                );
            }

            this._configItemsToolbar.push('-');

            if(hideItems.indexOf('search') < 0) {
                this._configItemsToolbar.push('Buscar por :');
                this._configItemsToolbar.push(' ');
                this._configItemsToolbar.push(this.getKeywordField());
                this._configItemsToolbar.push('-');
            }

            this._configItemsToolbar.push('->');

            if(hideItems.indexOf('download') < 0) {
                this._configItemsToolbar.push('-');
                this._configItemsToolbar.push(
                    {
                        text: 'Download',
                        iconCls: 'icon-core icon-core-csv',
                        scope: this,
                        handler: this.doDownload
                    }
                );
            }
        }

        return this._configItemsToolbar;
    },

    openItem: function() {
        console.debug('Não Implementado')
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg,{
            openItemFunction: this.openItem
        });

        Ext.apply(cfg,{
            columnAction: false,
        });

        edocs.processo.referencia.Grid.superclass.constructor.call(this, cfg);
    }

})
