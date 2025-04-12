/**
 *
 **/
Ext._define('edocs.processo.admin.processoAdminGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'edocs.processo.admin.processoAdminWindow',

    keywordFieldMessage: '',

    hideItemsToolbar: ['remove', 'download'],

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Protocolo', dataIndex: 'codigo', width: 130, hidden: true, sortable: true},
                    {header: 'Processo', dataIndex: 'codigo_processo', width: 160, sortable: true},
                    {header: "P. Externo", dataIndex: 'protocolo_externo', width: 130, hidden: true, sortable: true},
                    {header: "Movimentado", dataIndex: "movimentado", sortable: true},
                    {header: "Assunto", dataIndex: "assunto_display", width: 180, sortable: true},
                    {header: "Custo", dataIndex: "custo", sortable: true, width: 70},
                    {header: "Remetente", dataIndex: "remetente", width: 200},
                    {header: "Localização atual", dataIndex: "posicao", id: 'autoExpandColumn'},
                    {header: "Situação", dataIndex: "situacao_display", width: 180, sortable: true},
                    {header: 'Página', dataIndex: 'paginas', width: 60, sortable: true},
                    {header: 'Volume', dataIndex: 'volume', width: 50, sortable: true},
                ]
            );

        return this._columnModel;
    },

    createItem: function(values) {
        if(!this.allowCreate)
            return

        values = core.nullValue(values, {});

        this.factoryRestfulWindow({
            action: 'create',
            params: {manual: true},
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

    updateItem: function(record) {
        if(!this.allowUpdate)
            return;

        if(record instanceof Ext.Button)
            record = undefined;

        var selected = core.nullValue(record, this.getSelectionModel().getSelected());

        if(selected) {
            // if(selected.get('passo') != 0) {  //diferente
            //     Ext.Msg.show({
            //         title: 'Editando',
            //         icon: Ext.Msg.ERROR,
            //         buttons: Ext.Msg.OK,
            //         msg: 'Não é possível modificar um processo movimentado!'
            //     });
            // }
            // else{
            this.factoryRestfulWindow({
                action: 'update',
                oId: selected.get('id'), //id = protocolo.pk
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
            // }
        }
        else
            Ext.Msg.show({
                title: 'Editando',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item para editar.'
            });
    },

    getConfigItemsToolbar: function() {
        var menu = [];
        menu.push({
            text: "Novo",
            iconCls: true,
            icon: "/" + global.Context + "/static/images/add.png",
            handler: this.createItem,
            scope: this
        });
        menu.push({
            text: "Editar",
            iconCls: true,
            icon: "/" + global.Context + "/static/images/edit.png",
            handler: this.updateItem,
            scope: this
        });
        menu.push({
            text: "Excluir",
            iconCls: true,
            icon: "/" + global.Context + "/static/images/delete.png",
            handler: this.excluirItem,
            scope: this
        });
        menu.push("-");
        menu.push({
            text: "Abrir",
            iconCls: true,
            icon: "/" + global.Context + "/static/images/document-open.png",
            handler: function() {
                if(this.getSelectionModel().getSelected()) {
                    this.openItem();
                }
                else
                    Ext.Msg.show({
                        title: 'Visualizar',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Primeiro selecione um item.'
                    });
            },
            scope: this
        });
        menu.push({
            text: "Justificar",
            iconCls: true,
            icon: "/" + global.Context + "/static/images/document-sing.png",
            menu: [
            {
                text: "Redução de Página",
                iconCls: true,
                icon: "/" + global.Context + "/static/images/document-sing.png",
                handler: this.reduzirPagina,
                scope: this
            },
            {
                text: "Redução de Volume",
                iconCls: true,
                icon: "/" + global.Context + "/static/images/document-sing.png",
                handler: this.reduzirVolume,
                scope: this
            }
            ]
        });
        menu.push("-");
        menu.push({
            text: "Imprimir",
            iconCls: true,
            icon: "/" + global.Context + "/static/images/application-pdf.png",
            menu: [{
                text: "Todo andamento",
                iconCls: true,
                handler: this._imprimir_protocolo,
                scope: this
            }]
        });
        menu.push("-");
        menu.push("Busca Rápida : ");
        menu.push(" ");
        menu.push(this.getKeywordField());
        menu.push("-");
        return menu;
    },

    reduzirPagina: function() {
        var selected = this.getSelectionModel().getSelected();
        if(selected) {
            Ext._create('edocs.processo.justificativa.Window',{
                action: 'create',
                values: selected.data,
                disableSaveAndNew: true,
                params: {tipo: 1, processo: selected.get('id'), movimentacao: selected.get('movimentacao')},
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getStore().reload();
                        }
                    }
                },
            }).show();
        }
        else
            Ext.Msg.show({
                title: 'Rduzir Página',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Selecione um processo'
            });
    },

    reduzirVolume: function() {
        var selected = this.getSelectionModel().getSelected();
        if(selected) {
            Ext._create('edocs.processo.justificativa.Window',{
                action: 'create',
                values: selected.data,
                disableSaveAndNew: true,
                params: {tipo: 2, processo: selected.get('id'), movimentacao: selected.get('movimentacao')},
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getStore().reload();
                        }
                    }
                },
            }).show();
        }
        else
            Ext.Msg.show({
                title: 'Rduzir Volume',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Selecione um processo'
            });
    },

    _imprimir_protocolo: function() {
        var codigo;
        var selected = this.getSelectionModel().getSelected();
            if(selected) {
                codigo = selected.get("codigo");
                new toolkit.widget.ExtReportBuild(
                    // 'EDOCPrintAthenasProtocolo',
                    // '/to/mpe/protocolo/athenas/documento_movimentacoes'
                    'EPADPrintMovimentacao',
                    '/to/mpe/processo/movimentacao/documento_movimentacoes'
                ).runReport('',{protocolo:codigo});
            }
            else
                Ext.Msg.show({
                    title: 'Imprimir Protocolo',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Selecione um processo'
                });
    },

    openItem: function() {
        var selected = this.getSelectionModel().getSelected();
        if(selected) {
            Ext._create('edocs.processo.openWindow',{
                action: 'update',
                oId: selected.get('id'),
                values: selected.data,
                params: this.getParams(),
            }).show();
        }
    },

    excluirItem: function() {
        var selected = this.getSelectionModel().getSelected();

        if(selected) {
            if(selected.get('passo') != 0) {  //diferente
                Ext.Msg.show({
                    title: 'Excluir',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Não é possível excluir um processo movimentado!'
                });
            }
            else{
                Ext._create('edocs.processo.excluirWindow',{
                    action: 'update',
                    oId: selected.get('id'), //id = protocolo.pk
                    values: selected.data,
                    params: {excluido: true},
                    title: 'Excluir',
                    callback: {
                        success: {
                            scope: this,
                            fn: function() {
                                this.getStore().reload();
                            }
                        }
                    },
                }).show();
            }
        }
        else
            Ext.Msg.show({
                title: 'Excluir',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item.'
            });
    },

    doubleClick: function(grid) {
        var selected = this.getSelectionModel().getSelected();
        if(selected) {
            if(selected.get("passo") == 0)
                this.updateItem();
            else
                this.openItem();
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg,{
           autoExpandMin: 210,
        });

        Ext.apply(cfg,{
            doubleClickHandler: this.doubleClick,
            allowRemove: false,
            columnAction: false,
        });

        edocs.processo.admin.processoAdminGrid.superclass.constructor.call(this, cfg);
    }

});
