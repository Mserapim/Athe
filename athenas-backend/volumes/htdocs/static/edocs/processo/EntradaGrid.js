/**
 *
 **/
Ext._define('edocs.processo.EntradaGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'edocs.processo.Window',

    keywordFieldMessage: 'Realize sua busca por chancela ou código.',

    createItem: function(values) {
        if(!this.allowCreate)
            return;

        values = core.nullValue(values, {});

        this.factoryRestfulWindow({
            action: 'create',
            params: this.getParams(),
            callback: this.callback
        }).show();
    },

    updateItem: function(record) {
        if(!this.allowUpdate)
            return;

        if(record instanceof Ext.Button)
            record = undefined;

        var selected = core.nullValue(record, this.getSelectionModel().getSelected());

        if(selected) {
            if(selected.get('passo') != 0) {  //diferente
                Ext.Msg.show({
                    title: 'Editando',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Não é possível modificar um processo movimentado!'
                });
            }
            else{
                this.factoryRestfulWindow({
                    action: 'update',
                    oId: selected.get('id'), //id = protocolo.pk
                    values: selected.data,
                    params: this.getParams(),
                    callback: this.callback,
                }).show();
            }
        }
        else
            Ext.Msg.show({
                title: 'Editando',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item para editar.'
            });
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = this.createColumnModel();

        return this._columnModel;
    },

    getStore: function() {
        if(!this._store) {
            rest = this.factoryRestful();
            this._store = rest.getStore(false, false, {box: '1'});
        }

        return this._store;
    },

    getFooterbar: function(cfg) {
        if(!this._footerbar)
            this._footerbar = Ext._create('Ext.PagingToolbar', {
                style: cfg.footerStyle,
                store: this.getStore(),
                displayInfo: true,
                prependButtons: true
            });

        return this._footerbar;
    },

    createColumnModel: function() {
            var items = [];
            items.push({
                header: "Status",
                dataIndex: "status",
                sortable: false,
                width: 105,
                renderer: function(value) {
                    var tpl = new Ext.XTemplate(
                        "<div>",
                            "<tpl for=\"icons\">",
                            "<img style=\"margin-right:4px;width:12px;height:12px;)\" src=\"{url}\"/>",
                            "</tpl>",
                        "</div>"
                    );

                    var icons = [];
                    if(value) {
                        if(value.recebido)
                            icons.push({ url: toolkit.util.Normalize.controller_action( "static", "images") + "mail-mark-read.png"});
                        else icons.push({ url: toolkit.util.Normalize.controller_action( "static", "images") + "mail-mark-unread-new.png"});
                        if(value.attache) icons.push({url: toolkit.util.Normalize.controller_action("static","images") + "attachment.png"});
                        else icons.push({url: Ext.BLANK_IMAGE_URL});

                        if(value.urgente)
                            icons.push({ url: toolkit.util.Normalize.controller_action("static","images") + "mail-mark-important.png"});
                        else icons.push({url: Ext.BLANK_IMAGE_URL});

                        if(value.finalizado)
                            icons.push({url: toolkit.util.Normalize.controller_action("static","images") + "accept.png"});
                        else icons.push({ url: Ext.BLANK_IMAGE_URL });

                        if(value.compartilhado)
                            icons.push({ url: toolkit.util.Normalize.controller_action("static","images") + "document-open-remote.png"});
                        else icons.push({url: Ext.BLANK_IMAGE_URL });

                        if(value.locked)
                            icons.push({ url: toolkit.util.Normalize.controller_action("static","images") + "denied.png"});
                        else icons.push({url: Ext.BLANK_IMAGE_URL });
                    }
                    return tpl.apply({
                        "icons": icons
                    });
                }
            });
            items.push(
            {
                header: "Protocolo",
                dataIndex: "codigo",
                sortable: true,
                width: 130,
                hidden: true,
            });
            items.push({
                header: "Processo",
                dataIndex: "codigo_processo",
                sortable: true,
                width: 160
            });
            items.push({
                header: "P. Externo",
                dataIndex: "protocolo_externo",
                sortable: true,
                width: 130,
                hidden: true
            });
            items.push({
                header: "Movimentado",
                dataIndex: "data",
                sortable: true
            });
            items.push({
                header: "Primeiro Interessado",
                dataIndex: "primeiro_interessado",
                sortable: true,
                width: 200
            });
            items.push({
                header: "Assunto",
                dataIndex: "assunto_display",
                sortable: true,
                id: 'autoExpandColumn'
            });
            items.push({
                header: "Custo",
                dataIndex: "custo",
                sortable: true,
                width: 70
            });
            items.push({
                header: "Remetente",
                dataIndex: "origem",
                width: 200
            });
            items.push({
                header: "Localização atual",
                dataIndex: "posicao",
                width: 350
            });

            return new Ext.grid.ColumnModel(items);
        },

    getConfigItemsToolbar: function() {
        var menu = [];
        menu.push({
            text: "Abrir",
            iconCls: true,
            icon: "/" + global.Context + "/static/images/document-open.png",
            handler: function() {
                if(this.getSelectionModel().getSelected()) {
                    if(this.getSelectionModel().getSelected().get("passo") == 0)
                        this.updateItem();
                    else
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
        menu.push("-");
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
            text: "Receber",
            scope: this,
            icon: "/" + global.Context + "/static/images/mail-mark-read.png",
            handler: function() {
                var movs = [];
                var selection = this.getSelectionModel().getSelections();
                if(selection.length != 0) {
                    Ext.each(selection, function(record) { movs.push(record.get('movimentacao')); });
                    this.receber(movs);
                }
                else{
                    Ext.Msg.show({
                        title: 'Receber',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Selecione pelo menos um item.'
                    });
                }
            }
         });
        menu.push({
            text: "Movimentar",
            iconCls: true,
            icon: "/" + global.Context + "/static/images/view-sort-ascending.png",
            handler: this.movimentar,
            scope: this
        });
        menu.push({
            text: "Modificar Assunto",
            iconCls: true,
            icon: "/" + global.Context + "/static/images/document-sing.png",
            handler: this.subject,
            scope: this
        });
        menu.push({
            text: "Lote",
            iconCls: true,
            icon: "/" + global.Context + "/static/engine/images/icons/athenas-0142.png",
            scope: this,
            menu:[
             {
                text: "Movimentar",
                scope: this,
                icon: "/" + global.Context + "/static/images/view-sort-ascending.png",
                handler: function() {
                    var movs = [];
                    var selection = this.getSelectionModel().getSelections();
                    if(selection.length != 0) {
                        var error = Ext.each(selection,
                                function(mov) {
                                    movs.push(mov.get('movimentacao'));
                                    return(this.verifica_perm_envio(mov));
                                },
                                this
                                );
                        if(error == undefined) {
                            var situacao_locked = Ext.each(selection,
                                function(mov) {
                                    return !mov.get('status').situacao_locked;
                                },
                                this
                                );
                            if (situacao_locked == undefined) {
                                this.movimentar_lote(movs, false);
                            }
                            else{
                                this.movimentar_lote(movs, true);
                            }
                        }
                    }
                    else {
                        Ext.Msg.show({
                            title: 'Movimentar Lote',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: 'Selecione pelo menos um item.'
                        });
                    }
                }
             },
            ]
        });
        menu.push("-");
        menu.push({
            text: "Imprimir",
            iconCls: true,
            icon: "/" + global.Context + "/static/images/application-pdf.png",
            menu: this._get_menu_imprimir()
        });
        menu.push("-");
        menu.push("Busca Rápida : ");
        menu.push(" ");
        menu.push(this.getKeywordField());
        menu.push("-");
        return menu;
    },

    _get_menu_imprimir: function() {
        var menu = [];
        // menu.push({
        //     text: "Etiqueta (alterar)",
        //     iconCls: true,
        //     handler: this.imprimir_etiqueta,
        //     scope: this
        // });
        menu.push({
            text: "Todo andamento",
            iconCls: true,
            handler: function() { this._imprimir_protocolo();},
            scope: this
        });

        return menu;
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

    imprimir_etiqueta: function() {
        var selected = this.getSelectionModel().getSelected();
        if(selected) {
            Ext._create('edocs.processo.ImprimirForm',{
                action: 'create',
                params: {movimentacao: selected.get('movimentacao')},
            }).show();
        }
        else
            Ext.Msg.show({
                title: 'Imprimir Etiqueta',
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
                single: false,
                caixa: 1,
                callback: this.callback,
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

    verifica_perm_envio: function(selected) {
        perm_envio = true;

        if (selected.get('status').encaminhado == true) {
            perm_envio = false;
            message = 'O processo ' + selected.get('codigo_processo') + '  já foi enviado!';
        }
        if (selected.get('status').finalizado == true) {
            perm_envio = false;
            message = 'O processo ' + selected.get('codigo_processo') + ' já foi finalizado!';
        }
        if(selected.get('status').compartilhado == true) {
            perm_envio = false;
            message = 'O processo ' + selected.get('codigo_processo') + ' foi apenas compartilhado!';
        }
        if (perm_envio == false) {
            Ext.Msg.show({
                title: 'Movimentar',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: message
            });
            return false;

        }
        if (selected.get('status').recebido == false) {
            Ext.Msg.show({
                title: 'Movimentar',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'O processo ' + selected.get('codigo_processo') + ' ainda não foi recebido!'
            });
            return false;
        }
        if(perm_envio == true && selected.get('status').recebido == true) {
            return true;
        }
        else
            return false;
    },

    subject: function() {
        var selected = this.getSelectionModel().getSelected();
        if(selected) {
            if(this.verifica_perm_envio(selected) == true)
                Ext._create('edocs.processo.SubjectWindow', {
                    action: 'create',
                    modal: true,
                    process: selected.get('id'),
                    callback: {
                        success: {
                            scope: this,
                            fn: function(instance) {
                                core.invokeCallback((this.callback || {}).success);
                                this.close();
                            }
                        }
                    }
                }).show();

        } else{
            Ext.Msg.show({
                title: 'Modificar Assunto',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Selecione um processo!'
            });
        }
    },

    movimentar: function() {
        var selected = this.getSelectionModel().getSelected();
        if(selected) {
            if(this.verifica_perm_envio(selected) == true) {
                Ext._create('edocs.processo.movimentarWindow',{
                    action: 'create',
                    oId: selected.get('id'),
                    situacao_locked: selected.get('status').situacao_locked,
                    params: {protocolo: selected.get('codigo'), movimentacao: selected.get('movimentacao')},
                    callback: this.callback,
                }).show();
            }
        }
        else{
            Ext.Msg.show({
                title: 'Movimentar',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Selecione um processo!'
            });
        }
    },

    movimentar_lote: function(movs, situacao_locked) {
        Ext._create('edocs.processo.movimentarLoteWindow',{
            action: 'create',
            situacao_locked: situacao_locked,
            params: {selecteds: movs},
            callback: this.callback,
        }).show();
    },

    receber: function(movs) {
        conf = {
            scope: this,
            method: 'GET',
            url: core.callAction("EpadMovimentacao", "action_receber_movimentacoes", movs),
            success: function(request) {
                var rst = Ext.decode(request.responseText);
                if(rst.success) {
                    this.getStore().reload();
                }
                else {
                    Ext.Msg.show({
                        title: 'Receber',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: rst.message
                    });
                }
            },
            failure: function(request) {
                console.debug('Falha na requisição');
            },
        };
        Ext.Ajax.request(conf);
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

        Ext.applyIf(
            cfg,
            {
                autoExpandMin: 210,
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
                viewConfig:{
                    getRowClass: function(record, rowIndex, rp, ds) { // rp = rowParams
                      if(record.data.status.recebido == false)
                        return 'rowRed';
                      else
                        return 'rowGreen';
                    }
                },
                doubleClickHandler: this.doubleClick,
                border: false,
                columnAction: false,
            }
        );

        edocs.processo.EntradaGrid.superclass.constructor.call(this, cfg);

        // this.on({
        //     scope: this,
        //     rowclick: function(obj, rowIndex, e) {
        //         var selected = this.getSelectionModel().getSelected();
        //         if(selected) {
        //             this.father._detail.manageSelectProcess(selected);
        //         }
        //     }
        // });

    }

});
