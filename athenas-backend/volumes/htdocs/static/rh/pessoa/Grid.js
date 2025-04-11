/**
 *
 **/
Ext._define('rh.pessoa.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.pessoa.Window',

    keywordFieldMessage: 'Nome, cpf ou cnpj (somente números)',

    hideItemsToolbar: ['edit', 'remove'],

    getColumnModel: function(){
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Nome', dataIndex: 'nome', width: 260, sortable:true},
                    {header: 'CPF/CNPJ', dataIndex: 'cpf_cnpj', id: 'autoExpandColumn', sortable: true},
                    {header: 'Modificado por', dataIndex: 'modified_by_unicode', width: 120, hidden: true, sortable: true},
                    {header: 'Criado em', dataIndex: 'created_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), hidden: true, sortable: true},
                    {header: 'Modificado em', dataIndex: 'modified_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), hidden: true, sortable: true},
                    {header: 'Criado por', dataIndex: 'created_by_unicode', width: 120, hidden: true, sortable: true}
                ]
            );

        return this._columnModel;
    },

    getActionColumn: function() {
        if(!this._actionColumn)
            this._actionColumn = Ext._create('Ext.grid.ActionColumn', {
                width: 70,
                scope: this,
                items: [
                    {
                        iconCls: 'icon-16px icon-core icon-core-delete',
                        tooltip: 'Remover item.',
                        handler: function(action, index) {
                            var record = this.getStore().getAt(index);
                            record && this.defaultRemoveFunction(record);
                        }
                    }
                ]
            });

        return this._actionColumn;
    },

    createPessoaFisica: function() {
        if(!this.allowCreate){
            console.debug('allowCreate desabilitado')
            return
        }

        Ext._create('rh.pessoa.fisica.Window',{
            action: 'create',
            title: 'Nova pessoa física',
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

    },

    createPessoaJuridica: function() {
        if(!this.allowCreate){
            console.debug('allowCreate desabilitado')
            return
        }

        Ext._create('rh.pessoa.juridica.Window',{
            action: 'create',
            title: 'Nova pessoa jurídica',
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
                        menu:[
                            {
                                text: 'Pessoa Fisica',
                                iconCls: 'icon-core icon-core-add',
                                scope: this,
                                handler: this.createPessoaFisica,
                            },
                            {
                                text: 'Pessoa Juridica',
                                iconCls: 'icon-core icon-core-add',
                                scope: this,
                                handler: this.createPessoaJuridica,
                            }
                        ],
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

            if(hideItems.indexOf('search') < 0){
                this._configItemsToolbar.push('Buscar por :');
                this._configItemsToolbar.push(' ');
                this._configItemsToolbar.push(this.getKeywordField());
                this._configItemsToolbar.push('-');
            }

            this._configItemsToolbar.push('->');

            if(hideItems.indexOf('download') < 0){
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

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg,{
            columnAction: false,
            defaultRemoveFunction: this.removeItems,
        });

        Ext.apply(cfg,{
            allowUpdate: false,
            allowRemove: false,
        });

        rh.pessoa.Grid.superclass.constructor.call(this, cfg);
    }

})
