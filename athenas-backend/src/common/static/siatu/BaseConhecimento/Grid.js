/**
 *
 **/
Ext._define('common.siatu.BaseConhecimento.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'common.siatu.BaseConhecimento.Window',

    keywordFieldMessage: 'Objeto, problema ou solução',

    getColumnModel: function(){
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Codigo', dataIndex: 'pk', width: 60, sortable:true},
                    {header: 'Objeto', dataIndex: 'objeto_string', width: 100, sortable:true},
                    {header: 'Modelo', dataIndex: 'modelo_string', width: 100, sortable:true},
                    {header: 'Problema', dataIndex: 'problema', width: 160},
                    {header: 'Solução', dataIndex: 'solucao', id: 'autoExpandColumn'},
                    {header: 'Arquivo', dataIndex: 'filename', width: 150},
                ]
            );

        return this._columnModel;
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

            if(hideItems.indexOf('search') < 0){
                this._configItemsToolbar.push('Buscar por :');
                this._configItemsToolbar.push(' ');
                this._configItemsToolbar.push(this.getKeywordField());
                this._configItemsToolbar.push('-');
            }

            this._configItemsToolbar.push(this.getDownloadButton());
            this._configItemsToolbar.push('->');
        }

        return this._configItemsToolbar;
    },

    getDownloadButton: function() {
        if(!this._downloadButton)
            this._downloadButton = Ext._create('Ext.Button', {
                text: 'Download',
                iconCls: 'icon-siatu icon-siatu-move-down',
                scope: this,
                handler: this.download
            });

        return this._downloadButton;
    },

    download: function() {
        var selected = this.getSelectionModel().getSelected();
        if (selected){
            if (selected.get('arquivo') != 0){
                open(selected.get('permalink','_self'))
            }
        }
        else{
            Ext.Msg.show({
                title: 'Anexo',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item para efetuar download.'
            });
        }
    },

    filterInformatica: function(checked, autoload) {
        autoload = core.nullValue(autoload, true);
        this.filtroInformatica = checked;
        this.setFilterProperty('objeto__informatica', this.filtroInformatica, 1000, autoload)
        data = new Date()
        data.setYear(data.getYear() + 1902)
        Ext.util.Cookies.set('siatu-area-informatica', Ext.encode(this.filtroInformatica), data);
    },

    getFilterMenu: function(cfg) {
        if (!this._filterMenu){
            this._filterMenu = [
                {
                    text: 'Área de Informática',
                    checked: this.filtroInformatica,
                    scope: this,
                    listeners: {
                        scope: this,
                        checkchange: function(btn, checked) {
                            this.filterInformatica(checked);
                        }
                    }
                }
            ]
        }
        return this._filterMenu
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            hideItemsToolbar: ['remove', 'download']
        });

        Ext.apply(cfg,{
            columnAction: false,
            allowRemove: false,
        });

        if (Ext.util.Cookies.get('siatu-area-informatica') != null)
            this.filtroInformatica = Ext.decode(Ext.util.Cookies.get('siatu-area-informatica'));
        else
            this.filtroInformatica = false;

        common.siatu.BaseConhecimento.Grid.superclass.constructor.call(this, cfg);
        this.setFilterProperty('objeto__informatica', this.filtroInformatica, 1000 , false)

        this.getSelectionModel().on({
            scope: this,
            rowselect: function(grid, index, record) {
                if (record.get('arquivo') != 0){
                    this.getDownloadButton().enable()
                }
                else{
                    this.getDownloadButton().disable()
                }
            }
        })
    }

})
