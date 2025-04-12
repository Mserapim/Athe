/**
 *
 **/
Ext._define('common.siatu.chamado.ItemBaseConhecimento.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'common.siatu.chamado.ItemBaseConhecimento.Window',

    keywordFieldMessage: 'Objeto, problema ou solução',

    getColumnModel: function(){
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Codigo', dataIndex: 'base_conhecimento', width: 50, sortable:true},
                    {header: 'Objeto', dataIndex: 'objeto_string', width: 95, sortable:true},
                    {header: 'Problema', dataIndex: 'problema', width: 135},
                    {header: 'Solução', dataIndex: 'solucao', width: 135},
                    {header: 'Qtde', dataIndex: 'info', id: 'autoExpandColumn'}
                ]
            );

        return this._columnModel;
    },

    updateItem: function(record) {
        if(!this.allowUpdate)
            return

        if(record instanceof Ext.Button)
            record = undefined;

        var selected = core.nullValue(record, this.getSelectionModel().getSelected());

        if(selected) {
            this.factoryRestfulWindow({
                action: 'update',
                oId: selected.get('pk'),
                disableSave: this.disableSave,
                values: selected.data,
                params: this.getParams(),
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getStore().reload();
                        }
                    }
                }
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

    getConfigItemsToolbar: function(cfg){
        hideItems = cfg.hideItemsToolbar || this.hideItemsToolbar;
        if(!this._configItemsToolbar){
            this._configItemsToolbar = [];
            if(hideItems.indexOf('add') < 0){
                this._configItemsToolbar.push(
                    {
                        text: 'Novo',
                        iconCls: 'icon-core icon-core-add',
                        scope: this,
                        handler: this.createItem,
                    }
                );
            }
            if(hideItems.indexOf('edit') < 0){
                this._configItemsToolbar.push(
                    {
                        text: 'Editar',
                        iconCls: 'icon-core icon-core-edit',
                        scope: this,
                        handler: this.updateItem,
                    }
                );
            }
            if(hideItems.indexOf('remove') < 0){
                this._configItemsToolbar.push(
                    {
                        text: 'Remover',
                        iconCls: 'icon-core icon-core-delete',
                        scope: this,
                        handler: this.removeItems,
                    }
                );
            }

            this._configItemsToolbar.push('-');

            if(hideItems.indexOf('base_conhecimento') < 0){
                this._configItemsToolbar.push('Buscar:');
                this._configItemsToolbar.push(this.getBaseConhecimentoField());
                this._configItemsToolbar.push('-');
            }

            if(hideItems.indexOf('search') < 0){
                this._configItemsToolbar.push('Buscar por :');
                this._configItemsToolbar.push(' ');
                this._configItemsToolbar.push(this.getKeywordField());
                this._configItemsToolbar.push('-');
            }

            if(hideItems.indexOf('download') < 0){
                this._configItemsToolbar.push('->');
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

    getBaseConhecimentoField: function(){
        if(!this._baseConhecimento){
            if (Ext.util.Cookies.get('siatu-area-informatica') != null)
                this.filtroInformatica = Ext.decode(Ext.util.Cookies.get('siatu-area-informatica'));
            else
                this.filtroInformatica = false;
            this._baseConhecimento = Ext._create('core.fields.AutocompleteField', {
                rest: 'common.siatu.BaseConhecimento.Restful',
                name: 'base_conhecimento',
                fieldLabel: 'Item',
                emptyText: 'Selecione um item para inserir',
                allowBlank: true,
                width: 255,
                preFilter: [{property: 'objeto__informatica', value: this.filtroInformatica, stage: 1000}],
                gridConfig: {
                    allowUpdate: false,
                    allowRemove: false,
                    listeners: {
                        scope: this,
                        render: function(grid){
                            tbar = grid.getToolbar()
                            tbar.remove(tbar.getComponent(1))//Editar
                            tbar.remove(tbar.getComponent(1))//Remover
                        },
                    }
                },
                comboListeners: {
                    scope: this,
                    changevalid:function(cmb, id, start, valid, old) {
                        if(valid == true){
                            base_conhecimento = cmb.getValue()
                            var rest = this.factoryRestful();
                            rest.create(
                                {
                                    params: {
                                        chamado: this.getParams().chamado,
                                        base_conhecimento: base_conhecimento,
                                    },
                                    externalCallback: {
                                        success: {
                                            scope: this,
                                            fn: function(){
                                                this.getStore().load({})
                                            }
                                        }
                                    }
                                }
                            );
                            this.OldValueCombo = cmb.getValue()
                            this.getBaseConhecimentoField().reset()
                        }

                    },
                },
            });
        }

        return this._baseConhecimento;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        common.siatu.chamado.ItemBaseConhecimento.Grid.superclass.constructor.call(this, cfg);
    }

})
