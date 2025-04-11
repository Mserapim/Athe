/**
 *
 **/
Ext._define('edocs.processo.SaidaGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'edocs.processo.Window',

    keywordFieldMessage: 'Realize sua busca por chancela ou código.',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = this.createColumnModel();

        return this._columnModel;
    },

    getStore: function() {
        if(!this._store) {
            rest = this.factoryRestful();
            this._store = rest.getStore(false, false, {box: '2'});
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

    getConfigItemsToolbar: function(cfg) {
        var menu = [];
        menu.push(
            {
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
            },
            "-",
            {
                text: "Desfazer envio",
                iconCls: true,
                icon: "/" + global.Context + "/static/images/undo-icon.png",
                scope: this,
                handler: function() {
                    var selected = this.getSelectionModel().getSelected();
                    if(selected) {
                        if(!selected.get('status').compartilhado) {
                            Ext.Msg.show({
                                scope: this,
                                title: 'PERGUNTA',
                                icon: Ext.Msg.QUESTION,
                                buttons: Ext.Msg.OKCANCEL,
                                msg: 'Deseja realmente desfazer os envios do processo '+ selected.get('codigo_processo') +' ?',
                                fn: function(button) {
                                    if(button=='ok') {
                                        this.desfazer_envio(selected);
                                    }
                                },
                            });
                        }
                        else
                            Ext.Msg.show({
                            title: 'Desfazer envio',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: 'Este processo foi apenas compartilhado.'
                        });
                    }
                    else
                        Ext.Msg.show({
                            title: 'Desfazer envio',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: 'Primeiro selecione um item.'
                        });
                },
            },
            "-",
            {
                text: "Imprimir",
                iconCls: true,
                icon: "/" + global.Context + "/static/images/application-pdf.png",
                menu: this._get_menu_imprimir()
            },
            "-",
            "Busca Rápida : ",
            " ",
            this.getKeywordField()
        );

        return menu;
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
                hidden: true
            });
            items.push({
                header: "Processo",
                dataIndex: "codigo_processo",
                sortable: true,
                width: 130
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
                width: 180
            });
            items.push({
                header: "Remetente",
                dataIndex: "origem",
                width: 200
            });
            items.push({
                header: "Localização atual",
                dataIndex: "posicao",
                minWidth: 200,
                id: 'autoExpandColumn'
            });

            return new Ext.grid.ColumnModel(items);
        },

    _get_menu_imprimir: function() {
        var menu = [];
        // menu.push({
        //     text: "Etiqueta (alterar)",
        //     iconCls: true,
        //     handler: this._outImprimir,
        //     scope: this
        // });
        menu.push({
            text: "Todo andamento",
            iconCls: true,
            handler: function() { this._imprimir_protocolo(); },
            scope: this
        });
        menu.push({
            text: "Recibo",
            iconCls: true,
            handler: this._imprimirRecibo,
            scope: this
        });

        return menu;
    },

    _imprimirRecibo: function() {
            var selections = this.getSelectionModel().getSelections();
            if(selections.length > 0) {
                var movSel = [];
                Ext.each(
                    selections,
                    function(record) {movSel.push(record.get('movimentacao'));}
                );
                new toolkit.widget.ExtReportBuild(
                    // 'EDOCPrintAthenasRecebimento',
                    // '/to/mpe/protocolo/athenas/recebimento/protocolo'
                    'EPADPrintAthenasRecebimento',
                    '/to/mpe/processo/recebimento/protocolo'
                ).runReport( '', { movimentacoes: movSel });
            }
            else
                Ext.Msg.show({
                    title: 'Imprimir Recibo',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Selecione pelo menos um processo'
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

    _outImprimir: function() {
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
                caixa: 2,
                single: false,
                callback: this.callback,
            }).show();
        }
    },

    desfazer_envio: function(selected) {
        conf = {
            scope: this,
            method: 'POST',
            url: core.callAction("EpadMovimentacao", "action_desfazer_envio"),
            params: {movimentacao: selected.get('movimentacao')},
            success: function(request) {
                var rst = Ext.decode(request.responseText);
                if(rst.success) {
                    core.invokeCallback(this.callback.success);
                }
                else {
                    Ext.Msg.show({
                        title: 'Desfazer envio',
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
            this.openItem();
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                viewConfig: {
                    getRowClass: function(record, rowIndex, rp, ds) { // rp = rowParams
                      if(record.data.status.recebido == false)
                        return 'rowRed';
                      else
                        return 'rowGreen';
                    }
                },
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
                doubleClickHandler: this.doubleClick,
                border: false,
                columnAction: false,
            }
        );

        edocs.processo.SaidaGrid.superclass.constructor.call(this, cfg);

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
