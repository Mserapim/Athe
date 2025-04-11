/**
 *
 **/
Ext._define('edocs.processo.openWindow', {
    extend: 'core.RestfulWindow',

    rest: 'edocs.processo.Restful',

    width: 700,

    actionTitles: {
        create: 'Novo Processo',
        update: 'Visualização do Processo',
        remove: 'Remover',
        read: 'Carregar'
    },

    getFormPanel: function() {
        var tpl = new Ext.XTemplate(
                "<table class=\"property\">",
                    "<tr>",
                        "<td class=\"field\"><font size=2>Num. Protocolo :</font></td>",
                        "<td><font size=2>{codigo}</font></td>",
                    "</tr>",
                    "<tr>",
                        "<td class=\"field\"><font size=2>Processo :</font></td>",
                        "<td><font size=2>{codigo_processo}</font></td>",
                    "</tr>",
                    "<tr>",
                        "<td class=\"field\"><font size=2>P. Externo :</font></td>",
                        "<td><font size=2>{protocolo_externo}</font></td>",
                    "</tr>",
                    "<tr>",
                        "<td class=\"field\"><font size=2>Tipo :</font></td>",
                        "<td class=\"value\"><font size=2>{tipo_documento_unicode}</font></td>",
                    "</tr>",
                    "<tr>",
                        "<td class=\"field\"><font size=2>Assunto :</font></td>",
                        "<td class=\"value\"><font size=2>{assunto_display}</font></td>",
                    "</tr>",
                    "<tr>",
                        "<td class=\"field\"><font size=2>Protocolado por :</font></td>",
                        "<td class=\"value\"><font size=2>{protocolado_por}</font></td>",
                    "</tr>",
                    "<tr>",
                        "<td class=\"field\"><font size=2>Volume :</font></td>",
                        "<td class=\"value\"><font size=2>{volume}</font></td>",
                    "</tr>",
                    "<tr>",
                        "<td class=\"field\"><font size=2>Página :</font></td>",
                        "<td class=\"value\"><font size=2>{paginas}</font></td>",
                    "</tr>",
                    "<tr>",
                        "<td class=\"field\"><font size=2>Situação :</font></td>",
                        "<td class=\"value\"><font size=2>{situacao_display}</font></td>",
                    "</tr>",
                    '<tpl if="caixa != 0">',
                    "<tr>",
                        "<td class=\"field\"><font size=2>Caixa :</font></td>",
                        "<td class=\"value\"><font size=2>{caixa}</font></td>",
                    "</tr>",
                    '</tpl>',
                    "<tr>",
                    "<td class=\"field\"><font size=2>Qtde de dias :</font></td>",
                    "<td class=\"value\"><font size=2>{dias_criacao}</font></td>",
                     "</tr>",
                    "<tr>",
                    "<td class=\"field\"><font size=2>Interessados :</font></td>",
                    "<td class=\"value\"><font size=2>",
                    '<tpl for="interessados">',
                        "{1} <br>",
                    '</tpl>',
                    "</font></td>",
                    "</tr>",
                    "<tr>",
                        "<td class=\"field\"><font size=2>Resumo :</font></td>",
                        "<td class=\"value\"></td>",
                    "</tr>",
                    "<tr>",
                        "<td colspan=\"2\" class=\"value\"><div style=\"height: 70px; width: 660px; overflow: auto; padding: 8px;\">{resumo}</div></td>",
                    "</tr>",
                "</table>"
            );
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: [
                    // ---- INICIO ----
                    new Ext.TabPanel({
                        height: 390,
                        width: 685,
                        activeTab: 0,
                        tabPosition: "bottom",
                        border: false,
                        items: [
                            {
                                xtype: 'panel',
                                autoScroll: true,
                                border: true,
                                title: 'Processo',
                                bodyStyle: "border:none;border-bottom:1px solid #99bbe8",
                                html: tpl.apply(this.values)
                            },
                            // ---------------------------- Grid Movimentações do Processo -----------------
                            this.getMovimentacoesGrid(),
                            // ---------------------------- Grid Anexos -----------------
                            this.getAnexosGrid(),
                            // ---------------------------- Grid Referencias -----------------
                            this.getReferenciasGrid(),
                            // ---------------------------- Grid Referenciado por -----------------
                            this.getReferenciadoPorGrid(),
                        ]
                    })
                    // ---- FIM ----
                ]
            });

        return this._formPanel;
    },

    receber: function(movs) {
        conf = {
            scope: this,
            method: 'GET',
            url: core.callAction("EpadMovimentacao", "action_receber_movimentacoes", movs),
            success: function(request) {
                var rst = Ext.decode(request.responseText);
                if(rst.success) {
                    this.getMovimentacoesStore().reload();
                    core.invokeCallback(this.callback.success);
                    this.values.status.recebido = true;
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

    getButtons: function(cfg) {
        if(!this._buttons) {
            this._buttons = [];
            if(this.caixa == 1) {
                this._buttons.push({
                    text: "Movimentar",
                    handler: this.movimentar,
                    scope: this
                });
                this._buttons.push({
                    text: "Receber",
                    scope: this,
                    handler: function() {
                        var movs = [this.values.movimentacao];
                        this.receber(movs);
                    }
                });
            }
            this._buttons.push({
                text: "Fechar",
                handler: this.destroy,
                scope: this
            });
        }

        return this._buttons;
    },

    getMovimentacoesGrid: function() {
        if (!this._movGrid)
            this._movGrid = Ext._create('Ext.grid.GridPanel',{
                showPreview: true, // custom property
                enableRowBody: true, // required to create a second, full-width row to show expanded Record data
                viewConfig:{
                    getRowClass: function(record, rowIndex, rp, ds) { // rp = rowParams
                      if(record.data.recebido=='') return 'rowRed';
                      else if(record.data.recebido!='') return 'rowGreen';
                      else return 'rowYellow';
                    }
                },
                title: "Histórico",
                tbar: [
                    {
                        text: "Ver Parecer",
                        iconCls: true,
                        icon: "/" + global.Context + "/static/engine/images/icons/athenas-0098.png",
                        handler: function() {
                            var selected = this.getMovimentacoesGrid().getSelectionModel().getSelected();
                            if(selected) {
                                this.showParecerWindow(selected.get('parecer'));
                            }
                            else
                                Ext.Msg.show({
                                    title: 'Parecer',
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK,
                                    msg: 'Selecione uma movimentação!'
                                });
                        },
                        scope: this
                    }
                ],
                border: false,
                store: this.getMovimentacoesStore(),
                sm: new Ext.grid.RowSelectionModel({ singleSelect: true }),
                cm: new Ext.grid.ColumnModel([
                    {dataIndex: "encaminhado_por",header: "Remetente", width: 200},
                    {dataIndex: "encaminhado", header: "Encaminhado", width: 100},
                    {dataIndex: "encaminhado_para",header: "Destinatário", width: 200},
                    {dataIndex: "volume",header: "Volume", width: 100},
                    {dataIndex: "paginas",header: "Página", width: 60},
                    {dataIndex: "situacao",header: "Situação", width: 100},
                    {dataIndex: "custo",header: "Custo", width: 70},
                    {dataIndex: "recebido",header: "Recebido", width: 100},
                    {dataIndex: "recebido_por",header: "Recebido por", width: 260}
                ]),
                bbar: new Ext.PagingToolbar({
                    store: this.getMovimentacoesStore(),       // grid and PagingToolbar using same store
                    displayInfo: true,
                    pageSize: 10,
                    prependButtons: true
                }),
                listeners: {
                    scope: this,
                    dblclick: function() {
                        var selected = this.getMovimentacoesGrid().getSelectionModel().getSelected();
                        if(selected) {
                            this.showParecerWindow(selected.get('parecer'));
                        }
                    }
                }
        });

        return this._movGrid;
    },

    showParecerWindow: function(parecer) {
        var tpl = new Ext.XTemplate(
            "<table class=\"property\">",
                "<tr>",
                    "<td><div style=\"height: 300px; width: 650px; overflow: auto; padding: 8px;\">{parecer}</div></td>",
                "</tr>",
            "</table>"
        );
        this.parecerWindow = new Ext.Window({
            title: "Visualização do Parecer",
            closable: true,
            modal: true,
            width: 600,
            items: [
                new Ext.Panel({
                    border: true,
                    bodyStyle: "border:none;border-bottom:1px solid #99bbe8",
                    html: tpl.apply({parecer: parecer})
                }),
            ],
            buttonAlign: "center",
            buttons: [
                {
                    text: "Fechar",
                    handler: function() { this.parecerWindow.destroy(); },
                    scope: this
                }
            ]
        });
        this.parecerWindow.show();
    },

    getMovimentacoesStore: function() {
        if(!this._movStore) {
            this._movStore = Ext._create('Ext.data.Store', {
                proxy: Ext._create('Ext.data.HttpProxy', {
                    api: {
                        read: core.callAction("EpadMovimentacao", "action_movimentacoes_processo", this.values.codigo)
                    },
                    disableCaching: false,
                }),
                reader: Ext._create('Ext.data.JsonReader', {
                    idProperty: 'pk',
                    root: 'collection',
                    totalProperty: 'count',
                    successProperty: 'success',
                    messageProperty: 'message',
                    fields: ['pk', 'encaminhado_por', 'encaminhado','encaminhado_para', 'recebido', 'recebido_por', 'parecer',
                            'volume', 'paginas', 'custo', 'situacao'],
                }),
                autoLoad: true
            });
        }
        return this._movStore;
    },

    getAnexosGrid: function() {
        if (!this._anexosGrid) {
            this._anexosGrid = Ext._create('edocs.protocolo.AttachmentGrid', {
                region: 'center',
                title: 'Anexos (0)',
                columnAction: false,
                gridAutoLoad: false,
                doubleClickHandler: function() {},
                configOrderToolBar: [],
            });

            this._anexosGrid.setFilterProperty('protocol', this.oId, 1, false);
            this._anexosGrid.getStore().load({scope: this, callback: this.posLoadAnexos});
        }

        return this._anexosGrid;
    },

    // Utilizado para aba Referencias
    // Vai abrir o processo referenciado pelo item que estamos visualizando (abre o selecionado)
    openProcessoReferenciado: function() {
        //  this == ReferenciasGrid
        //  this.parent == this
        var selected = this.getSelectionModel().getSelected();
        if (selected)
            this.parent.openProcesso(selected.get('referenciado_codigo_protocolo'));
    },

    // Utilizado para aba Referenciado_por
    // Vai abrir o processo que referencia o item que estamos visualizando (abre o selecionado)
    openProcessoReferenciando: function() {
        // this == Referenciado_porGrid
        // this.parent == this
        var selected = this.getSelectionModel().getSelected();
        if (selected)
            this.parent.openProcesso(selected.get('processo_codigo_protocolo'));
    },

    getReferenciasGrid:function() {
        if (!this._referenciasGrid) {
            this._referenciasGrid = Ext._create('edocs.processo.referencia.Grid',{
                openItemFunction: this.openProcessoReferenciado,
                doubleClickHandler: this.openProcessoReferenciado,
                parent: this,
                gridAutoLoad: false,
                title: 'Referências (0)',
                hideItemsToolbar: ['search', 'download']
            });

            this._referenciasGrid.setFilterProperty('processo', this.oId, 1, false);
            this._referenciasGrid.setParam('processo', this.oId);
            this._referenciasGrid.getStore().load({scope: this, callback: this.posLoadReferencias});
        }

        return this._referenciasGrid;
    },

    getReferenciadoPorGrid:function() {
        if (!this._referenciadoPorGrid) {
            this._referenciadoPorGrid = Ext._create('edocs.processo.referencia.Grid', {
                openItemFunction: this.openProcessoReferenciando,
                doubleClickHandler: this.openProcessoReferenciando,
                parent: this,
                gridAutoLoad: false,
                title: 'Referenciado por (0)',
                hideItemsToolbar: ['add', 'edit', 'remove', 'search', 'download']
            });

            this._referenciadoPorGrid.reconfigure(
                this._referenciadoPorGrid.getStore(),
                Ext._create('Ext.grid.ColumnModel', [
                    {header: 'Processo', dataIndex: 'processo_codigo', width: 100},
                    {header: 'Tipo', dataIndex: 'tipo_display', width: 100},
                    {header: 'Descrição', dataIndex: 'descricao', id: 'autoExpandColumn'},
                ]
            ));

            this._referenciadoPorGrid.setFilterProperty('referenciado', this.oId, 1, false);
            this._referenciadoPorGrid.getStore().load({scope: this, callback: this.posLoadReferenciadoPor});
        }

        return this._referenciadoPorGrid;
    },

    open: function(values) {
        Ext._create('edocs.processo.openWindow',{
            action: 'update',
            values: values,
            oId: values.id,
            single: this.single,
            caixa: 0,
            callback: {
                success: {
                    scope: this,
                    fn: function() {
                    }
                }
            }
        }).show();
    },

    openProcesso: function(codigo) {
        var rest = Ext._create('edocs.processo.Restful', {});
        var restSingle = Ext._create('edocs.processo.consulta.processoComumRestful', {});
        conf = {
            scope: this,
            success: function(request) {
                var rst = Ext.decode(request.responseText);
                if(rst.success) {
                    this.open(rst.instance);
                }
                else {
                    Ext.Msg.show({
                        title: 'Visualização',
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

        if (this.single == true) {
            restSingle.doRequest(restSingle.getRoute('action_open_processo', codigo, null, conf));
        } else {
            rest.doRequest(rest.getRoute('action_open_processo', codigo, null, conf));
        }
    },

    movimentar: function() {
        perm_envio = true;
        if (this.values.status.encaminhado == true) {
            perm_envio = false;
            message = 'Este protocolo já foi enviado!';
        }
        if (this.values.status.finalizado == true) {
            perm_envio = false;
            message = 'Este protocolo já foi finalizado!';
        }
        if (perm_envio == false) {
            Ext.Msg.show({
                title: 'Movimentar',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: message
            });

        }
        if (this.values.status.recebido == false) {
            Ext.Msg.show({
                title: 'Movimentar',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Este protocolo ainda não foi recebido!'
            });

        }
        if(perm_envio == true && this.values.status.recebido == true) {
            Ext._create('edocs.processo.movimentarWindow', {
                action: 'create',
                oId: this.oId,
                situacao_locked: this.values.status.situacao_locked,
                params: {protocolo: this.values.codigo, movimentacao: this.values.movimentacao},
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getMovimentacoesStore().reload();
                            core.invokeCallback(this.callback.success);
                        }
                    }
                }
            }).show();
        }
    },

    posLoadAnexos: function(records) {
        this.getAnexosGrid().setTitle('Anexos (' + records.length + ')');
    },

    posLoadReferencias: function(records) {
        this.getReferenciasGrid().setTitle('Referências (' + records.length + ')');
    },

    posLoadReferenciadoPor: function(records) {
        this.getReferenciadoPorGrid().setTitle('Referenciado por (' + records.length + ')');
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        this.caixa = cfg.caixa;
        this.values = core.nullValue(cfg.values, {});
        this.oId = cfg.oId;

        Ext.applyIf(cfg, {
            single: true
        });

        Ext.apply(cfg, {
            buttonAlign: 'center',
        });

        edocs.processo.openWindow.superclass.constructor.call(this, cfg);
    },
});
