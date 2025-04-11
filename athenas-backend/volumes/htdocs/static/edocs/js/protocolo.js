
if(typeof(toolkit) == "undefiend" || typeof(toolkit.util) == "undefined" || typeof(toolkit.widget)) {

    toolkit.edocs.protocolo = {};

    toolkit.edocs.protocolo.Box = function(geral) {
        this.stores = {
            "in": undefined,
            "out": undefined,
            "movimentar": undefined,
            "movimentos": undefined
        };

        this.geral = (geral == undefined ? false : geral);
        this.buscaIn = undefined;
        this.buscaOut = undefined;
    }

    toolkit.edocs.protocolo.Box.prototype = {

        stores: {
            "in": undefined,
            "out": undefined,
            "movimentar": undefined,
            "movimentos": undefined
        },

        getOutBox: function() {
            if(this.panelOut == undefined) {
                this.panelOut = new Ext.Panel({
                    title: "Saída",
                    border: false,
                    items: [this.getGridPanelOut()]
                });
            }

            return this.panelOut;
        },

        _not_implemented: function() {
            console.debug("Não implementado");
        },

        _get_menu_imprimir: function(box){
            var menu = [];
            if(this.geral){
                menu.push({
                    text: "Etiqueta",
                    iconCls: true,
                    handler: box == 2 ? this._outImprimir : this._not_implemented,
                    scope: this
                });
            }
            menu.push({
                text: "Protoclo",
                iconCls: true,
                handler: function(){ this._imprimir_protocolo(box)},
                scope: this
            });
            if(box == 2){
                menu.push({
                    text: "Recibo",
                    iconCls: true,
                    handler: this._imprimirRecibo,
                    scope: this
                });
            }
            return menu;
        },

        _finalizar: function(){
            if(this.getGridPanelIn().getSelectionModel().getSelected()){
                if(!this.getGridPanelIn().getSelectionModel().getSelected().get("status").compartilhado){
                    if(confirm("Deseja realmente finalizar o protocolo "+this.getGridPanelIn().getSelectionModel().getSelected().get("codigo")+" ?")){
                        Ext.Ajax.request({
                            url: toolkit.util.Normalize.controller_action(
                                "EDOCBox",
                                "finalizar"
                            ),
                            params: {
                                movimentacao: this.getGridPanelIn().getSelectionModel().getSelected().get("movimentacao"),
                                protocolo: this.getGridPanelIn().getSelectionModel().getSelected().get("codigo"),
                                concluir: "on"
                            },
                            method: 'POST',
                            scope: this,
                            success: function(request) {
                                var code = Ext.util.JSON.decode(request.responseText);
                                if(!code.success)
                                    alert(code.msg);
                                else{
                                    //TODO: MODIFICADO AQUI 30/08/2010
                                    if(this.buscaIn != undefined){
                                        this.stores["in"].load({params:{start: 0, limit: 30, valor: this.buscaIn}});
                                        this.stores["out"].load({params:{start: 0, limit: 30, valor: this.buscaOut}});
                                    }
                                    else{
                                        this.stores["in"].load({params:{start: 0, limit: 30}});
                                        this.stores["out"].load({params:{start: 0, limit: 30}});
                                    }
                                }
                            },
                            failure: function(form, action) {
                                alert("Não foi possivel resgatar informações no servidor. Tente novamente mais tarde.");
                            }
                        });
                    }
                }else alert("Este protocolo foi apenas compartilhado!");
            }else alert("Selecione um Protocolo!");
        },

        _desfazer_envio: function(){
            if(this.getGridPanelOut().getSelectionModel().getSelected()){
                if(!this.getGridPanelOut().getSelectionModel().getSelected().get("status").compartilhado){
                    if(confirm("Deseja realmente desfazer os envios do protocolo "+this.getGridPanelOut().getSelectionModel().getSelected().get("codigo")+" ?")){
                        Ext.Ajax.request({
                            url: toolkit.util.Normalize.controller_action(
                                "EDOCBox",
                                "desfazer_envio"
                            ),
                            params: { movimentacao: this.getGridPanelOut().getSelectionModel().getSelected().get("movimentacao") },
                            method: 'POST',
                            scope: this,
                            success: function(request) {
                                var code = Ext.util.JSON.decode(request.responseText);
                                if(code.success == false) alert(code.msg);
                                this.getInStore();
                                this.getOutStore().reload();
                            },
                            failure: function() { alert("Não foi possivel resgatar informações no servidor. Tente novamente mais tarde."); }
                        });
                    }
                }else alert("Este protocolo foi apenas compartilhado!");
            }else alert("Selecione um Protocolo!");
        },

        _imprimirRecibo: function() {
            var sm = this.getGridPanelOut().getSelectionModel();
            if(sm.getSelections().length > 0) {
                var movSel = [];
                Ext.each(
                    sm.getSelections(),
                    function(record) {movSel.push(record.get('movimentacao'));}
                );
                new toolkit.widget.ExtReportBuild(
                    'EDOCPrintAthenasRecebimento',
                    '/to/mpe/protocolo/athenas/recebimento/protocolo'
                ).runReport( '', { movimentacoes: movSel })
            }else alert('Selecione pelo menos uma linha da movimentação.');
        },

        _imprimir_protocolo: function(box) {
            var codigo = undefined;
            try{
                if(box == 1) codigo = this.getGridPanelIn().getSelectionModel().getSelected().get("codigo");
                else if(box == 2) codigo = this.getGridPanelOut().getSelectionModel().getSelected().get("codigo");
                if(codigo != undefined) {
                    new toolkit.widget.ExtReportBuild(
                        'EDOCPrintAthenasProtocolo',
                        '/to/mpe/protocolo/athenas/documento_movimentacoes'
                    ).runReport('',{protocolo:codigo})
                }else alert("Selecione um Protocolo!");
            }catch(e){ alert("Selecione um Protocolo!"); }
        },

        _new: function(from) {
            var f = new toolkit.edocs.protocolo.BFormNew(this, from);
            f.show();
        },

        _inConfig: function() {
            new toolkit.edocs.protocolo.ConfigFormNew().show();
        },

        _newMov: function(codigo, movimentacao, caixa, father) {
            var f;
            if( caixa == undefined){
                if(this.getGridPanelIn().getSelectionModel().getSelected()){
                    if(!this.getGridPanelIn().getSelectionModel().getSelected().get("status").compartilhado){
                        if(father != undefined){
                            f = new toolkit.edocs.protocolo.MovFormNew(father, this.getGridPanelIn().getSelectionModel().getSelected().get("codigo"),
                                this.getGridPanelIn().getSelectionModel().getSelected().get("movimentacao"));
                            f.show();
                        }else{
                            f = new toolkit.edocs.protocolo.MovFormNew(this, this.getGridPanelIn().getSelectionModel().getSelected().get("codigo"),
                                this.getGridPanelIn().getSelectionModel().getSelected().get("movimentacao"));
                            f.show();
                        }
                    }else alert("Este protocolo foi apenas compartilhado!");
                }else alert("Selecione um Protocolo!");
            }else{
                f = new toolkit.edocs.protocolo.MovFormNew(this, codigo, movimentacao);
                f.show();
            }
        },

        _newMovLote: function(codigo, movimentacao, caixa, father) {
            var f;
            if(this.getGridPanelIn().getSelectionModel().getSelected()){
                if(!this.getGridPanelIn().getSelectionModel().getSelected().get("status").compartilhado){
                    var s = this.getGridPanelIn().getSelectionModel().getSelections();
                    var selecteds = [];
                    for(var i = 0, len = s.length; i < len; i++){ selecteds.push(s[i].get("movimentacao")); }
                    f = new toolkit.edocs.protocolo.MovProtLote(this, selecteds);
                    f.show();
                }else alert("Este protocolo foi apenas compartilhado!");
            }else alert("Selecione pelo menos um Protocolo!");
        },

        _openProtocoloFormView: function(box, codigo, movimentacao) {
//            novo/editando = -1
//            in = 1
//            out = 2
            //demais caixas com parâmetros
            if(box == -1){ this._new(codigo); }
            else if( (codigo != undefined) && (movimentacao != undefined)){
                new toolkit.edocs.protocolo.ProtocoloFormView(
                    this,
                    codigo,
                    movimentacao,
                    this.geral,
                    box
                ).show();
            }
            else if(box == 1){
                if(this.getGridPanelIn().getSelectionModel().getSelected()){
                    new toolkit.edocs.protocolo.ProtocoloFormView(
                        this,
                        this.getGridPanelIn().getSelectionModel().getSelected().get("codigo"),
                        this.getGridPanelIn().getSelectionModel().getSelected().get("movimentacao"),
                        this.geral,
                        box
                    ).show();
                }else alert("Selecione um item na caixa de entrada.");
            }
            else if(box == 2){
                if(this.getGridPanelOut().getSelectionModel().getSelected()){
                    new toolkit.edocs.protocolo.ProtocoloFormView(
                        this,
                        this.getGridPanelOut().getSelectionModel().getSelected().get("codigo"),
                        this.getGridPanelOut().getSelectionModel().getSelected().get("movimentacao"),
                        this.geral,
                        box
                    ).show();
                }else alert("Selecione um item na caixa de saida.");
            }else alert("Não foi possível realizar esta operação!");
        },

        _inImprimir: function() {
            alert("Só é possível imprimir a partir da caixa de saída!");
        },

        _outImprimir: function() {
            if(this.getGridPanelOut().getSelectionModel().getSelected()){
                var f = new toolkit.edocs.protocolo.ImprimirFormNew(this, this.getGridPanelOut().getSelectionModel().getSelected().get("movimentacao"));
                f.show();
            }else alert("Selecione um Protocolo!");
        },

        _excluir: function() {
            if(this.getGridPanelIn().getSelectionModel().getSelected()){
                if(!this.getGridPanelIn().getSelectionModel().getSelected().get("status").compartilhado){
                    if(confirm("Deseja realmente excluir este protocolo "+this.getGridPanelIn().getSelectionModel().getSelected().get("codigo")+" ?"))
                        this.commit_excluir(this.getGridPanelIn().getSelectionModel().getSelected().get("codigo"));
                }else alert("Este protocolo foi apenas compartilhado!");
            }else alert("Selecione um Protocolo!");
        },

        _get_menu_in_box: function(box){
            var menu = [];
            menu.push({
                text: "Abrir",
                iconCls: true,
                icon: "/" + global.Context + "/static/images/document-open.png",
                handler: function() {
                    if(this.gridPanelIn.getSelectionModel().getSelected()){
                        if(this.gridPanelIn.getSelectionModel().getSelected().get("passo") == 0)
                            this._openProtocoloFormView(-1, this.gridPanelIn.getSelectionModel().getSelected().get("codigo"),
                                this.gridPanelIn.getSelectionModel().getSelected().get("movimentaco"));
                        else this._openProtocoloFormView(1, undefined, undefined)
                    }else this._openProtocoloFormView(1, undefined, undefined);
                },
                scope: this
            });
            menu.push("-");
            menu.push({
                text: "Novo",
                iconCls: true,
                icon: "/" + global.Context + "/static/images/add.png",
                handler: function(){ this._new(undefined) },
                scope: this
            });
            menu.push({
                text: "Editar",
                iconCls: true,
                icon: "/" + global.Context + "/static/images/edit.png",
                handler: function(){
                    if(this.getGridPanelIn().getSelectionModel().getSelected())
                        this._new(this.getGridPanelIn().getSelectionModel().getSelected().get('codigo'));
                    else alert('Tente abrir um documento que ainda está em edição!');
                },
                scope: this
            });
            menu.push({
                text: "Excluir",
                iconCls: true,
                icon: "/" + global.Context + "/static/images/delete.png",
                handler: this._excluir,
                scope: this
            });
            menu.push("-");
            menu.push({
                text: "Receber",
                scope: this,
                icon: "/" + global.Context + "/static/images/mail-mark-read.png",
                handler: function(){
                    var movs = [];
                    var selection = this.getGridPanelIn().getSelectionModel().getSelections();
                    if(this.getGridPanelIn().getSelectionModel().getSelected()){
                        Ext.each(selection, function(mov) { movs.push(mov.get('movimentacao')) });
                        toolkit.edocs.protocolo.ProtocoloFormView.prototype.receber(movs, this.stores);
                    }else alert('Não existe nenhum protocolo selecionado.');
                }
             });
            menu.push("-");
            menu.push({
                text: "Movimentar",
                iconCls: true,
                icon: "/" + global.Context + "/static/images/view-sort-ascending.png",
                handler: this._newMov,
                scope: this
            });
            if(!this.geral){
                menu.push("-");
                menu.push({
                    text: "Marcar não recebido",
                    scope: this,
                    icon: "/" + global.Context + "/static/images/mail-mark-unread-new.png",
                    handler: function(){
                        var movs = [];
                        var selection = this.getGridPanelIn().getSelectionModel().getSelections();
                        Ext.each(selection, function(mov) { movs.push(mov.get('movimentacao')) });
                        toolkit.edocs.protocolo.ProtocoloFormView.prototype.marcar_nao_recebido(movs, this.stores);
                    }
                 });
            }
            else if(this.geral){
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
                        handler: this._newMovLote
                     },
                     {
                        text: "Receber",
                        scope: this,
                        icon: "/" + global.Context + "/static/images/mail-mark-read.png",
                        handler: function(){
                            var movs = [];
                            var selection = this.getGridPanelIn().getSelectionModel().getSelections();
                            Ext.each(selection, function(mov) { movs.push(mov.get('movimentacao')) });
                            toolkit.edocs.protocolo.ProtocoloFormView.prototype.receber(movs, this.stores);
                        }
                     },
                     {
                        text: "Marcar não recebido",
                        scope: this,
                        icon: "/" + global.Context + "/static/images/mail-mark-unread-new.png",
                        handler: function(){
                            var movs = [];
                            var selection = this.getGridPanelIn().getSelectionModel().getSelections();
                            Ext.each(selection, function(mov) { movs.push(mov.get('movimentacao')) });
                            toolkit.edocs.protocolo.ProtocoloFormView.prototype.marcar_nao_recebido(movs, this.stores);
                        }
                     }
                    ]
                });
            }
            menu.push("-");
            menu.push({
                text: "Finalizar",
                iconCls: true,
                icon: "/" + global.Context + "/static/images/accept.png",
                handler: function(){
                    this._finalizar();
                },
                scope: this
            });
            menu.push("-");
            menu.push({
                text: "Imprimir",
                iconCls: true,
                icon: "/" + global.Context + "/static/images/application-pdf.png",
                menu: this._get_menu_imprimir(1)
            });
            menu.push("-");
            menu.push("Busca Rápida : ");
            menu.push(" ");
            menu.push({
                xtype: "textfield",
                emptyText: "Realize sua busca por chancela ou código.",
                width: 250,
                enableKeyEvents: true,
                listeners: {
                    scope: this,
                    keypress: function(text, event) {
                        if (event.getCharCode() == event.RETURN || event.getCharCode() == event.TAB) {
                            this.buscaIn = text.getValue() == "" ? undefined : text.getValue();
                            this.stores["in"] = this.getInStore();
                        }
                    }
                }
            });
            menu.push("-");
            return menu;
        },

        getGridPanelOut: function() {
            if(!this.gridPanelOut) {
                this.gridPanelOut = new Ext.grid.GridPanel({
                    border: false,
                    colModel: this.createColumnModel(),
                    sm: new Ext.grid.RowSelectionModel({
                         singleSelect: false,
                         listeners: {
                             scope: this,
                             rowselect: function(sm) {
                                 var tpl = new Ext.XTemplate('Carregando as informações do resumo...');
                                 tpl.overwrite(this.getPreviewOut().body, {});

                                 Ext.Ajax.request({
                                    url: toolkit.util.Normalize.controller_action(
                                        'EDOCBox',
                                        'view',
                                        ['geral']
                                    ),
                                    mehtod: 'POST',
                                    params: { codigo: sm.getSelected().get('codigo') },
                                    scope: this,
                                    success: function(request) {
                                        var response = Ext.decode(request.responseText);
                                        var tpl = new Ext.XTemplate('<tpl if="resumo">{resumo}</tpl>');
                                        tpl.overwrite(this.getPreviewOut().body, response);
                                    }
                                 })
                             }
                         }
                    }),
                    store: this.getOutStore(),
                    tbar: [
                        {
                            text: "Abrir",
                            iconCls: true,
                            icon: "/" + global.Context + "/static/images/document-open.png",
                            handler: function() {this._openProtocoloFormView(2, undefined, undefined);},
                            scope: this
                        },
                        "-",
                        {
                            text: "Desfazer envio",
                            iconCls: true,
                            icon: "/" + global.Context + "/static/images/undo-icon.png",
                            handler: function() {this._desfazer_envio();},
                            scope: this
                        },
                        "-",
                        {
                            text: "Imprimir",
                            iconCls: true,
                            icon: "/" + global.Context + "/static/images/application-pdf.png",
                            menu: this._get_menu_imprimir(2)
                        },
                        "-",
                        "Busca Rápida : ",
                        " ",
                        {
                            xtype: "textfield",
                            emptyText: "Realize sua busca por chancela ou código.",
                            enableKeyEvents: true,
                            width: 250,
                            listeners: {
                                scope: this,
                                keypress: function(text, event) {
                                    if (event.getCharCode() == event.RETURN || event.getCharCode() == event.TAB) {
                                        var keyword = text.getValue();
                                        if (keyword != undefined && keyword != '')
                                            this.stores["out"].baseParams.valor = keyword;
                                        else
                                            this.stores["out"].baseParams.valor = undefined;
                                        this.stores["out"].reload({params: {start: 0, limit: 30}});
                                    }
                                }
                            }
                        },
                    ],
                    bbar: new Ext.PagingToolbar({
                        store: this.getOutStore(),       // grid and PagingToolbar using same store
                        displayInfo: true,
                        pageSize: 30,
                        prependButtons: true
                    }),
                    listeners: {
                        scope: this,
                        dblclick: function() {
                            if(this.getGridPanelOut().getSelectionModel().getSelected()){
                                this._openProtocoloFormView(2, undefined, undefined);
                            }//else alert("Não há registros!");
                        }
                    }
                });
                this.gridPanelOut.on({
                    render: function(p) {
                        new Ext.LoadMask(
                            p.getEl(),
                            {
                                msg: 'Carregando a caixa de entrada...',
                                store: p.getStore()
                            }
                        );
                    }
                });
            }

            return this.gridPanelOut
        },

        getGridPanelIn: function() {
            if(! this.gridPanelIn) {
                this.gridPanelIn = new Ext.grid.GridPanel({
                    border: false,
                    colModel: this.createColumnModel(),
                    sm: new Ext.grid.RowSelectionModel({
                         singleSelect: false,
                         listeners: {
                             scope: this,
                             rowselect: function(sm) {
                                 var tpl = new Ext.XTemplate('Carregando as informações do resumo...');
                                 tpl.overwrite(this.getPreviewIn().body, {});

                                 Ext.Ajax.request({
                                    url: toolkit.util.Normalize.controller_action(
                                        'EDOCBox',
                                        'view',
                                        ['geral']
                                    ),
                                    mehtod: 'POST',
                                    params: { codigo: sm.getSelected().get('codigo') },
                                    scope: this,
                                    success: function(request) {
                                        var response = Ext.decode(request.responseText);
                                        var tpl = new Ext.XTemplate('<tpl if="resumo">{resumo}</tpl>');
                                        tpl.overwrite(this.getPreviewIn().body, response)
                                    }
                                 })
                             }
                         }
                    }),
                    store: this.getInStore(),
                    tbar: this._get_menu_in_box(),
                    bbar: new Ext.PagingToolbar({
                        store: this.getInStore(),       // grid and PagingToolbar using same store
                        displayInfo: true,
                        pageSize: 30,
                        prependButtons: true
                    }),
                    listeners: {
                        scope: this,
                        dblclick: function() {
                            if(this.getGridPanelIn().getSelectionModel().getSelected()){
                                this._openProtocoloFormView(1, undefined, undefined);
                            }
                        }
                    }
                });

                this.gridPanelIn.on({
                    render: function(p) {
                        new Ext.LoadMask(
                            p.getEl(),
                            {
                                msg: 'Carregando a caixa de entrada...',
                                store: p.getStore()
                            }
                        );
                    }
                });
            }


            return this.gridPanelIn
        },

        getInBox: function() {
            if(this.panelIn == undefined) {
                this.panelIn = new Ext.Panel({
                    title: "Entrada",
                    border: false,
                    items: [this.getGridPanelIn()]
                });
            }
            return this.panelIn;
        },

        commit_excluir: function(codigo) {
            var obj = toolkit.util.Ajax.request_json(
                "POST",
                toolkit.util.Normalize.controller_action(
                    "EDOCBox",
                    "commit",
                    ["delete_protocolo"]
                ),
                {protocolo: codigo}
            );
            if(obj.result) try{ this.stores["in"].reload(); }catch(err){;}
            else alert(obj.message);
        },

        /**
         * Cria um formulário para edição de um item selecionado na GRID.
         **/
        action_edit: function(id, movimentacao) {
            if(id) {
                var frm = new toolkit.edocs.protocolo.MovFormNew(this, id, movimentacao);
                frm.show();
            }else alert("Primeiro você deve selecionar um item na lista.");
        },

        getPreviewIn: function() {
            if(!this.previewIn) {
                this.previewIn = new Ext.Panel({
                    border: false,
                    autoScroll: true
                });
            }
            return this.previewIn;
        },

        getPreviewOut: function() {
            if(!this.previewOut) {
                this.previewOut = new Ext.Panel({
                    border: false,
                    autoScroll: true
                });
            }
            return this.previewOut;
        },

        getPageGridIn: function() {
            if(!this.pageGridIn) {
                this.pageGridIn = new Ext.Panel({
                    title: "Entrada",
                    border: false,
                    layout: 'border',
                    items: [
                        {
                            region: 'center',
                            border: false,
                            layout: 'fit',
                            bodyStyle: 'border-bottom: 1px solid #99BBE8',
                            items: [ this.getInBox().getComponent(0) ]
                        },
                        {
                            region: 'south',
                            layout: 'fit',
                            height: 150,
                            minHeight: 0,
                            maxHeight: 200,
                            split: true,
                            border: false,
                            autoScroll: true,
                            bodyStyle: 'border-top: 1px solid #99BBE8;padding:2px',
                            items: [this.getPreviewIn()]
                        }
                    ]
                });
            }

            return this.pageGridIn;
        },

        getPageGridOut: function() {
            if(!this.pageGridOut) {
                this.pageGridOut = new Ext.Panel({
                    title: "Enviados",
                    border: false,
                    layout: 'border',
                    items: [
                        {
                            region: 'center',
                            border: false,
                            layout: 'fit',
                            bodyStyle: 'border-bottom: 1px solid #99BBE8',
                            items: [ this.getOutBox().getComponent(0) ]
                        },
                        {
                            region: 'south',
                            layout: 'fit',
                            height: 150,
                            minHeight: 0,
                            maxHeight: 200,
                            split: true,
                            border: false,
                            autoScroll: true,
                            bodyStyle: 'border-top: 1px solid #99BBE8;padding:2px',
                            items: [this.getPreviewOut()]
                        }
                    ]
                });
            }

            return this.pageGridOut;
        },

        show: function() {
            var ts = toolkit.Application.tabspace;
            this.panel = new Ext.Panel({
                title: "Caixa de Protocolo - E-DOC",
                closable: true,
                border: true,
                layout: "fit",
                items: [
                    new Ext.TabPanel({
                        activeTab: 0,
                        autoRender: true,
                        tabPosition: "top",
                        border: false,
                        items: [
                            this.getPageGridIn(),
                            this.getPageGridOut(),
                        ]
                    })
                ]
            });

            this.panelIn.on(
                "render",
                function() {
                    this.panelIn.doLayout();
                    this.panelIn.setHeight(this.panel.getBox().height - 30);
                    this.getGridPanelIn().setHeight(this.panel.getBox().height - 30);
                },
                this
            );

            this.panelOut.on(
                "render",
                function() {
                    this.panelOut.doLayout();
                    this.panelOut.setHeight(this.panel.getBox().height - 30);
                    this.getGridPanelOut().setHeight(this.panel.getBox().height - 30);
                },
                this
            );

            ts.remove(ts.getActiveTab());
            ts.add(this.panel);
            ts.setActiveTab(this.panel);

//            var panel = this;
//
//            new toolkit.thread.Simple({
//                period: 60000,
//                handler: function() {
//                    panel.getInStore();
//                    //TODO: MODIFICAR PARA UM MÉTODO EXCLUSIVO DE ATUALIZAÇÃO, NA VIEW UTILIZAR O DECORATOR @update_timeout_session(enable = False)
//                }
//            }).start();

            this.panel.doLayout();
        },

        getInStore: function() {
            if(this.stores["in"] == undefined) {
                this.stores["in"] = new Ext.data.JsonStore({
                    fields: [
                        "codigo",
                        "protocolo_externo",
                        "chancela",
                        "midia",
                        "data",
                        "interessado",
                        "assunto",
                        "origem",
                        "posicao",
                        "movimentacao",
                        "status",
                        "passo"
                    ],
                    root: "result",
                    totalProperty: "totalRows",
                    url: toolkit.util.Normalize.controller_action(
                        "EDOCBox",
                        "get_store",
                        ["in"]
                    ),
                    remoteSort: true
                });

                if(this.buscaIn != undefined) this.stores["in"].load({params:{ start: 0, limit: 30, valor: this.buscaIn }});
            }else{
                if(this.buscaIn != undefined) this.stores["in"].load({params:{ start: 0, limit: 30, valor: this.buscaIn }});
                else this.stores["in"].load({ params:{start: 0, limit: 30 }});
            }
            return this.stores["in"];
        },

        getInStoreMovimentar: function(id_protocolo) {
            if(id_protocolo != "-1"){
                this.stores["movimentar"] = new Ext.data.JsonStore({
                    fields: [
                        "local",
                        "interessado",
                        "data"
                    ],
                    root: "result",
                    url: toolkit.util.Normalize.controller_action(
                        "EDOCBox",
                        "get_store",
                        ["movimentar", id_protocolo]
                    ),
                    baseParams: {start: 0},
                    remoteSort: true
                });
                this.stores["movimentar"].load();
            }
            return this.stores["movimentar"];
        },

        getOutStore: function() {
            if(this.stores["out"] == undefined) {
                this.stores["out"] = new Ext.data.JsonStore({
                    fields: [
                        "codigo",
                        "protocolo_externo",
                        "chancela",
                        "midia",
                        "data",
                        "interessado",
                        "assunto",
                        "origem",
                        "posicao",
                        "movimentacao",
                        "status",
                        "passo"
                    ],
                    root: "result",
                    totalProperty: "totalRows",
                    url: toolkit.util.Normalize.controller_action(
                        "EDOCBox",
                        "get_store",
                        ["out"]
                    ),
                    remoteSort: true
                });
                this.stores["out"].load({ params:{ start: 0, limit: 30 } });
            }
            return this.stores["out"];
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
                header: "Código",
                dataIndex: "codigo",
                sortable: true,
                width: 130
            });
            if(this.geral){
                items.push({
                    header: "P. Externo",
                    dataIndex: "protocolo_externo",
                    sortable: true,
                    width: 130
                });
                items.push({
                    header: "Chancela",
                    dataIndex: "chancela",
                    allowBlank: false,
                    sortable: true,
                    width: 100
                });
                items.push({
                    header: "Mídia",
                    dataIndex: "midia",
                    allowBlank: true,
                    validateOnBlur: true,
                    sortable: true,
                    width: 60
                });
            }
            items.push({
                header: "Data",
                dataIndex: "data",
                sortable: true
            });
            items.push({
                header: "Interessado",
                dataIndex: "interessado",
                sortable: true,
                width: 215
            });
            items.push({
                header: "Assunto",
                dataIndex: "assunto",
                sortable: true,
                width: 180
            });
            items.push({
                header: "Origem",
                dataIndex: "origem",
                width: 200
            });
            items.push({
                header: "Posição",
                dataIndex: "posicao",
                width: 200
            });

            return new Ext.grid.ColumnModel(items);
        },

        createColumnModelMovimentar: function() {
            return new Ext.grid.ColumnModel([{ header: "Local", dataIndex: "local", width: 50}]);
        }
    }

    toolkit.edocs.protocolo.BFormNew = function(father, from) {
        this.father = father;
        this.from = from;
    },

    toolkit.edocs.protocolo.BFormNew.prototype = {

        commit: function() {
            var form = this.form.getForm();
            var values = form.getValues();
            if(this.from) values.codigo = this.from;
            var obj = toolkit.util.Ajax.request_json(
                "POST",
                toolkit.util.Normalize.controller_action(
                    "EDOCBox",
                    "validate",
                    ["novo_protocolo"]
                ),
                values
            );

            if(!obj.result) {
                for(var i in obj.errors) {
                    if(!isNaN(i)) {
                        var error = obj.errors[i];
                        var field = form.findField(error.field);
                        if(field) field.markInvalid();
                    }
                }
            }
            else {
                obj = toolkit.util.Ajax.request_json(
                    "POST",
                    toolkit.util.Normalize.controller_action(
                        "EDOCBox",
                        "commit",
                        ["novo_protocolo"]
                    ),
                    values
                );
                if(obj.result) this.father.stores["in"].reload();
                else alert(obj.message);
            }
            return obj.result;
        },

        getStore: function(store, codigo){
            var obj = toolkit.util.Ajax.request_json(
                "POST",
                toolkit.util.Normalize.controller_action(
                    "EDOCBox",
                    "get_store",
                    [store]
                ),
                {codigo: codigo}
            );
            return obj;
        },

        getFormPanel: function(store) {
            var width = 550;
            var height_multiselect_geral = 100;
            var height_multiselect_departamento = 100;
            if(store) store = store.result;
            if(this.form == undefined) {
                this.form = new Ext.form.FormPanel({
                    // width: 710,
                    border: false,
                    buttonAlign: "right",
                    buttons: [
                        {
                            text: "Salvar rascunho",
                            handler: function(){ if(this.commit()) this.wnd.destroy();},
                            scope: this
                        },
                        {
                            text: "Movimentar",
                            handler: function(){
                                if(store){
                                    if(this.commit()){
                                        var f = new toolkit.edocs.protocolo.MovFormNew(this.father, this.father.gridPanelIn.getSelectionModel().getSelected().get("codigo"),
                                            this.father.gridPanelIn.getSelectionModel().getSelected().get("movimentacao"));
                                        f.show();
                                    }
                                }else alert("Salve o protocolo!");
                            },
                            scope: this
                        },
                        {
                            text: "Cancelar",
                            handler: function() { this.wnd.destroy(); },
                            scope: this
                        }
                    ],
                    listeners: {
                        scope: this,
                        afterlayout: function(container, layout) {
                            if(this.form.getComponent(0).baseCls == "x-tab-panel") {
                                var cmp = this.form.getComponent(0);

                                for(var idx = cmp.items.getCount(); idx >= 0; idx--) {
                                    var itm = cmp.getComponent(idx);
                                    cmp.setActiveTab(itm);
                                }
                            }
                        }
                    },
                    items: [
                        new Ext.TabPanel({
                            activeTab: 0,
                            width: 710,
                            height: (this.father.geral ? 455 : 395),
                            defaults: {
                                boxMinHeight: 320,
                                boxMaxHeight: 555
                            },
                            border: false,
                            items: [
                                {
                                    xtype: "panel",
                                    layout: "form",
                                    title: "Informações",
                                    border: false,
                                    style: "margin: 5pt",
                                    labelWidth: 120,
                                    scope: this,
                                    items: this.getGeral(store)
                                },
                                {
                                    xtype: "panel",
                                    layout: "form",
                                    title: "Anexos",
                                    border: false,
                                    style: "margin: 5pt",
                                    defaults: {
                                        width: 370
                                    },
                                    labelWidth: 120,
                                    items: [{
                                        width: width,
                                        height: (this.father.geral ? height_multiselect_geral : height_multiselect_departamento),
                                        name: "anexos",
                                        fieldLabel: "Anexos",
                                        xtype: "multiselectbox",
                                        toSearch: [],
                                        height: 280,
                                        model: { name: "Anexo", pkg: "protocolo.models"},
                                        conf: {
                                            canAdd: true,
                                            canEdi: true
                                        },
                                        controller: "EDOCAnexo",
                                        value: store == undefined ? [] : store[0].anexos
                                    }]
                                },
                                {
                                    xtype: "panel",
                                    layout: "form",
                                    title: "Referências",
                                    border: false,
                                    style: "margin: 5pt",
                                    defaults: { width: 370 },
                                    labelWidth: 120,
                                    items: [{
                                        width: width,
                                        height: (this.father.geral ? height_multiselect_geral : height_multiselect_departamento),
                                        name: "referencias",
                                        fieldLabel: "Referências",
                                        height: 280,
                                        xtype: "multiselectbox",
                                        toSearch: [],
                                        model: { name: "Referencia", pkg: "protocolo.models"},
                                        conf: {
                                            canAdd: true,
                                            canEdi: true
                                        },
                                        controller: "EDOCReferencia",
                                        value: store == undefined ? [] : store[0].referencias
                                    }]
                                }
                            ]
                        })
                    ]
                });
            }

            return this.form;
        },

        getGeral: function(store){
            var items = [];
            var width = 550;
            if(this.father.geral){
                items.push({
                    "width": width,
                    "displayField": "description",
                    "fieldLabel": "Origem",
                    "allowBlank": false,
                    "validateOnBlur": true,
                    "hiddenName": "orgao_geral_origem",
                    "valueField": "pk",
                    "triggerAction": "all",
                    "queryAction": "query",
                    "model": "OrgaoGeral",
                    "hideTrigger": true,
                    "queryParam": "keyword",
                    "crudController": "RHOrgaoGeral",
                    "xtype": "autocompletefield",
                    "conf": {
                        "canAdd": true,
                        "canEdit": true
                    },
                    "value": store == undefined ? "" : store[0].orgao_geral_origem[0]
                });
                items.push({
                    "width": width,
                    "displayField": "description",
                    "allowBlank": false,
                    "validateOnBlur": true,
                    "fieldLabel": "Interessado",
                    "hiddenName": "interessado",
                    "valueField": "pk",
                    "triggerAction": "all",
                    "queryAction": "query",
                    "model": "Pessoa",
                    "hideTrigger": true,
                    "queryParam": "keyword",
                    "crudController": "RHPessoa",
                    "xtype": "autocompletefield",
                    "conf": {
                        "canAdd": true,
                        "canEdit": true
                    },
                    "value": store == undefined ? "" : store[0].interessado[0]
                });
                items.push({
                    width: width,
                    xtype: "textfield",
                    name: "chancela",
                    allowBlank: false,
                    validateOnBlur: true,
                    maxLenght: 12,
                    fieldLabel: "Chancela",
                    value: store == undefined ? "" : store[0].chancela
                });
            }
            if(this.father.geral){
                items.push({
                    width: width,
                    allowBlank: true,
                    hiddenName: "midia",
                    fieldLabel: "Mídia",
                    xtype: "combo",
                    displayField: "description",
                    valueField: "id",
                    store: toolkit.util.Ajax.request_json(
                        "POST",
                        toolkit.util.Normalize.controller_action(
                            "EDOCBox",
                            "get_store",
                            ["midia"]
                        )
                    ),
                    triggerAction: "all",
                    mode: 'local',
                    value: store == undefined ? "" : store[0].midia[0]
                });
            }else{
                items.push({
                    width: width,
                    allowBlank: false,
                    validateOnBlur: true,
                    hiddenName: "orgao_geral_origem",
                    fieldLabel: "Origem",
                    xtype: "combo",
                    displayField: "description",
                    valueField: "id",
                    store: toolkit.util.Ajax.request_json(
                        "POST",
                        toolkit.util.Normalize.controller_action(
                            "EDOCBox",
                            "get_store",
                            ["orgao_geral_origem"]
                        )
                    ),
                    triggerAction: "all",
                    mode: 'local',
                    value: store == undefined ? "" : store[0].orgao_geral_origem[0]
                });
            }
            items.push({
                width: width,
                allowBlank: false,
                validateOnBlur: true,
                hiddenName: "tipo_documento",
                fieldLabel: "Espécie",
                xtype: "combo",
                displayField: "description",
                valueField: "id",
                store: toolkit.util.Ajax.request_json(
                    "POST",
                    toolkit.util.Normalize.controller_action(
                        "EDOCBox",
                        "get_store",
                        ["tipo_documento"]
                    )
                ),
                triggerAction: "all",
                mode: 'local',
                value: store == undefined ? "" : store[0].tipo_documento[0]
            });
            items.push({
                width: width,
                allowBlank: false,
                validateOnBlur: true,
                xtype: "textfield",
                name: "assunto",
                maxLenght: 255,
                fieldLabel: "Assunto",
                value: store == undefined ? "" : store[0].assunto
            });
            items.push({
                width: width,
                name: "numero_externo",
                fieldLabel: "Número Externo",
                xtype: "textfield",
                value: store == undefined ? "" : store[0].protocolo_externo
            });
            items.push({
                name: "sigiloso",
                fieldLabel: "Sigiloso",
                xtype: "checkbox",
                value: store == undefined ? "" : store[0].sigiloso
            });
            items.push(new Ext.Panel({
                layout:'form',
                labelAlign: "top",
                border: false,
                items:[
                    new toolkit.plugins.CKEditor({
                        name:'resumo',
                        fieldLabel:'Corpo texto(4000 caracteres)',
			            value: store == undefined ? "" : store[0].resumo,
                        toolbar: [
                            ['Source'], ['PasteFromWord'],
                            ['Link','Unlink','Anchor'],
                            ['NumberedList','BulletedList'],
                            ['Bold','Italic','Underline', 'Styles','Format', 'TextColor','BGColor']
                        ],
                        autoScroll:true,
                        width:675,
                        height:105
                    })
		]
            }));
            return items;
        },

        show: function() {
            if(this.from){
                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action(
                        "EDOCBox",
                        "get_store/dados_protocolo"
                    ),
                    params: { codigo: this.from },
                    success: function(form, action){
                        var store = Ext.util.JSON.decode(form.responseText);
                        if(store.result[0].passo == 1){
                            this.wnd = new Ext.Window({
                                title: "Editando Protocolo",
                                closable: true,
                                modal: true,
                                'width': 705,
                                items: [ this.getFormPanel( Ext.util.JSON.decode(form.responseText) ) ]
                            });
                            this.wnd.show();
                        }else alert('Não é possível modificar um documento movimentado!');
                    },
                    failure: function(form, action){ alert('Dados não carregados'); },
                    scope: this
                });
            }else{
                this.wnd = new Ext.Window({
                    title: "Novo Protocolo",
                    closable: true,
                    modal: true,
                    'width': 705,
                    'resizable': false,
                    items: [ this.getFormPanel(undefined) ]
                });
                this.wnd.show();
            }
        }
    },

    /**
     * FORMULÁRIO PARA MOVIMENTAR PROTOCOLO
     */
    toolkit.edocs.protocolo.MovFormNew = function(father, codigo, movimentacao) {
       if(father != null) this.father = father;
        else throw new toolkit.widget.ExtNullPointerException("Bug: O objeto pai é requirido.");
        if(codigo != null){
            var data = toolkit.util.Ajax.request_json(
                'POST',
                toolkit.util.Normalize.controller_action(
                    "EDOCBox",
                    "carregar_protocolo"
                ),
                { codigo: codigo, movimentacao: movimentacao }
            );
        }else alet("Selecione um Protocolo!");

        this.recebido = false;
        this.perm_envio = false;
        if(data["perm_envio"]){
            this.perm_envio = true;
            if(data["result"][0].id) this.id = data["result"][0].id
            if(!data["result"][1].recebido) alert(data["result"][1].msg);
            else this.recebido = true;
            this.encaminhado = data["result"][2].encaminhado;
        }else alert(data["msg"]);
        this.movimentacao = movimentacao;
        this.codigo = codigo;
        this.objects = {};
    },


    toolkit.edocs.protocolo.MovFormNew.prototype = {

        commit: function() {
            var form = this.form.getForm();
            var values = form.getValues();
            values.protocolo = this.id;
            values.movimentacao = this.movimentacao;

            var obj = toolkit.util.Ajax.request_json(
                "POST",
                toolkit.util.Normalize.controller_action(
                    "EDOCBox",
                    "validate",
                    ["nova_movimentacao"]
                ),
                values
            );

            if(!obj.result) {
                for(var i in obj.errors) {
                    if(!isNaN(i)) {
                        var error = obj.errors[i];
                        var field = form.findField(error.field);
                        if(field) {
                            field.markInvalid();
                            if((field.name == "lotacao_destino") || (field.name == "pessoa")) alert(error.message);
                        }
                    }
                }
            }else {
                obj = toolkit.util.Ajax.request_json(
                    "POST",
                    toolkit.util.Normalize.controller_action(
                        "EDOCBox",
                        "commit",
                        ["nova_movimentacao"]
                    ),
                    values
                );
                if(obj.result) {
                    try{
                        this.father.stores["in"].reload();
                        this.father.stores["out"].reload();
                        if(this.father.stores["movimentos"] != undefined){
                            this.father.stores["movimentos"].reload();
                            this.father.stores["movimentos"] = undefined;
                        }
                    }catch(err){ console.debug(err); };
                    this.wnd.destroy();
                }else alert(obj.message);
            }
        },

        getFormPanel: function() {
            var width = 550;
            if(this.form == undefined) {
                this.formPanel = new Ext.Panel({
                    border: false,
                    buttonAlign: "right",
                    buttons: [
                        {
                            text: "Movimentar",
                            handler: this.commit,
                            scope: this
                        },
                        {
                            text: "Cancelar",
                            handler: function() { this.wnd.destroy(); },
                            scope: this
                        }
                    ],
                    items: [
                        this.form = new Ext.form.FormPanel({
                            border: false,
                            items: [
                                new Ext.TabPanel({
                                    activeTab: 0,
                                    // width: 600,
                                    'height': 360,
                                    border: false,
                                    defaults: { boxMinHeight: 320 },
                                    items: [
                                        {
                                            xtype: "panel",
                                            layout: "form",
                                            title: "Destinatário",
                                            border: false,
                                            style: "margin: 5pt",
                                            defaults: {
                                                width: 370
                                            },
                                            labelWidth: 120,
                                            items: this.get_destinatario_fields()
                                        },{
                                            xtype: "panel",
                                            layout: "form",
                                            title: "Informações",
                                            border: false,
                                            style: "margin: 5pt",
                                            labelWidth: 120,
                                            'labelAlign': 'top',
                                            items: [
                                                new toolkit.plugins.CKEditor({
                                                    name:'parecer',
                                                    fieldLabel:'Novo parecer',
                                                    toolbar: [
                                                        ['Source'], ['PasteFromWord'],
                                                        ['Link','Unlink','Anchor'],
                                                        ['NumberedList','BulletedList'],
                                                        ['Bold','Italic','Underline', 'Styles','Format', 'TextColor','BGColor']
                                                    ],
                                                    autoScroll:true,
                                                    width:680,
                                                    height:145
                                                }),
                                                {
                                                    'xtype': 'panel',
                                                    'layout': 'hbox',
                                                    'defaults': {
                                                        'height': 50,
                                                        'border': false
                                                    },
                                                    'border': false,
                                                    'width': 675,
                                                    'items': [
                                                        {
                                                            'xtype': 'panel',
                                                            'layout': 'form',
                                                            'flex': 1.0,
                                                            'items':  {
                                                                width: 120,
                                                                fieldLabel: "Deferido",
                                                                hiddenName: "deferido",
                                                                xtype: "combo",
                                                                store: new Ext.data.SimpleStore({
                                                                    fields: ["id", "desc"],
                                                                    data: [['None', '---------'], ['True', 'SIM'], ['False', 'NÃO']]
                                                                }),
                                                                valueField: "id",
                                                                displayField: "desc",
                                                                mode: "local",
                                                                triggerAction: "all"
                                                            }
                                                        },
                                                        {
                                                            'xtype': 'panel',
                                                            'layout': 'form',
                                                            'flex': 1.0,
                                                            'items':  {
                                                                name: "urgente",
                                                                boxLabel: "Pedir urgência",
                                                                // hideLabel: true,
                                                                xtype: "checkbox"
                                                            }
                                                        },
                                                        {
                                                            'xtype': 'panel',
                                                            'layout': 'form',
                                                            'flex': 1.0,
                                                            'items': {
                                                                name: "concluir",
                                                                boxLabel: "Finalizar movimentações",
                                                                // hideLabel: true,
                                                                xtype: "checkbox"
                                                            }
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                    {
                                        xtype: "panel",
                                        layout: "form",
                                        title: "Anexar",
                                        border: false,
                                        style: "margin: 5pt",
                                        defaults: { width: 370, height: 270 },
                                        labelWidth: 120,
                                        items: [{
                                            width: width,
                                            name: "anexos",
                                            fieldLabel: "Anexos (é possível apenas inserir novos anexos)",
                                            xtype: "multiselectbox",
                                            toSearch: [],
                                            model: { name: "Anexo", pkg: "protocolo.models" },
                                            conf: {
                                                canAdd: true,
                                                canEdi: true
                                            },
                                            controller: "EDOCAnexo"
                                        }]
                                    },
                                    {
                                        xtype: "panel",
                                        layout: "form",
                                        title: "Referências",
                                        border: false,
                                        style: "margin: 5pt",
                                        defaults: { width: 370, height: 270 },
                                        labelWidth: 120,
                                        items: [{
                                            width: width,
                                            name: "referencias",
                                            fieldLabel: "Referências",
                                            xtype: "multiselectbox",
                                            toSearch: [],
                                            model: { name: "Referencia", pkg: "protocolo.models" },
                                            conf: {
                                                canAdd: true,
                                                canEdi: true
                                            },
                                            controller: "EDOCReferencia"
                                        }]
                                    }
                                ]
                                })
                            ]
                        })
                    ]
                });

                this.form = this.formPanel.getComponent(0);
            }

            return this.formPanel;
        },

        get_destinatario_fields: function(){
            var width = 550;
            var items = [];
            items.push({
                width: width,
                name: "pessoa",
                fieldLabel: "Enviar p/ Pessoa",
                xtype: "multiselectbox",
                toSearch: [],
                allowBlank: true,
                validateOnBlur: true,
                height: 150,
                blankText: "É necessário preencher este campo.",
                model: { name: "PessoaFisica", pkg: "rh.models" },
                controller: "RHPessoaFisica",
                conf: {
                    canAdd: false,
                    canEdit: false
                },
                queryset: []
            });
            items.push({
                width: width,
                name: "lotacao_destino",
                fieldLabel: "Enviar p/ Lotação",
                xtype: "multiselectbox",
                toSearch: [],
                height: 150,
                allowBlank: true,
                validateOnBlur: true,
                blankText: "É necessário preencher este campo.",
                model: { name: "OrgaoGeral", pkg: "rh.models" },
                queryset: [],
                conf: {
                    canAdd: false,
                    canEdit: false
                },
                controller: this.father.geral == false ? "RHOrgaoGeralBuscaEspecial": "RHOrgaoGeral"
            });
            return items;
        },

        show: function() {
            if(this.recebido && !this.encaminhado && this.perm_envio){
                this.wnd = new Ext.Window({
                    title: "Nova Movimentação",
                    closable: true,
                    modal: true,
                    'width': 710,
                    'resizable': false,
                    items: [ this.getFormPanel() ]
                });
                this.wnd.show();
            }
        }
    },
    /**
     * FORMULÁRIO PARA MOVIMENTAR PROTOCOLOS EM LOTE
     */
    toolkit.edocs.protocolo.MovProtLote= function(father, selecteds) {

       if(father != null) this.father = father;
        else throw new toolkit.widget.ExtNullPointerException("Bug: O objeto pai é requirido.");
        if(selecteds != null){
            var data = toolkit.util.Ajax.request_json(
                'POST',
                toolkit.util.Normalize.controller_action(
                    "EDOCBox",
                    "permissao_protocolo"
                ),
                { selecteds: selecteds}
            );
        }else alet("Selecione um Protocolo!");

        this.perm_envio = false;
        if(data["perm_envio"]) this.perm_envio = true;
        else alert(data["msg"]);
        this.selecteds = selecteds;
        this.objects = {};
    },


    toolkit.edocs.protocolo.MovProtLote.prototype = {

        commit: function() {
            var form = this.form.getForm();
            var values = form.getValues();
            values.selecteds = this.selecteds;

            var obj = toolkit.util.Ajax.request_json(
                "POST",
                toolkit.util.Normalize.controller_action(
                    "EDOCBox",
                    "validate",
                    ["nova_movimentacao_lote"]
                ),
                values
            );
            if(!obj.result) {
                for(var i in obj.errors) {
                    if(!isNaN(i)) {
                        var error = obj.errors[i];
                        var field = form.findField(error.field);
                        if(field) {
                            field.markInvalid();
                            if((field.name == "lotacao_destino") || (field.name == "pessoa"))
                                if(error.message != "") alert(error.message);
                        }
                    }
                }
            }else {
                obj = toolkit.util.Ajax.request_json(
                    "POST",
                    toolkit.util.Normalize.controller_action(
                        "EDOCBox",
                        "commit",
                        ["nova_movimentacao_lote"]
                    ),
                    values
                );

                if(obj.success) {
                    try{
                        this.father.stores["in"].reload();
                        this.father.stores["out"].reload();
                        this.wnd.destroy();
                    }catch(err){ ; }
                    for(var i in obj.result) try{
                        if(parseInt(i)==i) alert(obj.result[i].msg);
                    }catch(e){;}
                    this.wnd.destroy();
                }else{
                    if(obj.msg != "") alert(obj.msg);
                }
            }
        },

        getFormPanel: function() {
            var width = 550;
            if(this.form == undefined) {
                this.formPanel = new Ext.Panel({
                    border: false,
                    buttonAlign: "right",
                    buttons: [
                        {
                            text: "Movimentar",
                            handler: this.commit,
                            scope: this
                        },
                        {
                            text: "Cancelar",
                            handler: function() { this.wnd.destroy(); },
                            scope: this
                        }
                    ],
                    items: [
                        this.form = new Ext.form.FormPanel({
                            border: false,
                            items: [
                                new Ext.TabPanel({
                                    activeTab: 0,
                                    width: 710,
                                    height: 455,
                                    border: false,
                                    items: [
                                        {
                                            xtype: "panel",
                                            layout: "form",
                                            title: "Informações",
                                            border: false,
                                            style: "margin: 5pt",
                                            labelWidth: 120,
                                            items: [
                                                new Ext.Panel({
                                                    layout:'form',
                                                    labelAlign: "top",
                                                    border: false,
                                                    items:[
                                                        new toolkit.plugins.CKEditor({
                                                            name:'parecer',
                                                            fieldLabel:'Novo parecer',
                                                            toolbar: [
                                                                ['Source'], ['PasteFromWord'],
                                                                ['Link','Unlink','Anchor'],
                                                                ['NumberedList','BulletedList'],
                                                                ['Bold','Italic','Underline', 'Styles','Format', 'TextColor','BGColor']
                                                            ],
                                                            autoScroll:true,
                                                            width:690,
                                                            height:310
                                                        })
                                                    ]
                                                })
                                            ]
                                    },
                                    {
                                        xtype: "panel",
                                        layout: "form",
                                        title: "Destinatário",
                                        border: false,
                                        style: "margin: 5pt",
                                        defaults: { width: 370 },
                                        labelWidth: 120,
                                        items: [
                                            {
                                                width: 555,
                                                name: "pessoa",
                                                fieldLabel: "Enviar p/ Pessoa",
                                                xtype: "multiselectbox",
                                                toSearch: [],
                                                allowBlank: true,
                                                validateOnBlur: true,
                                                height: 200,
                                                blankText: "É necessário preencher este campo.",
                                                model: { name: "PessoaFisica", pkg: "rh.models" },
                                                controller: "RHPessoaFisica",
                                                conf: {
                                                    canAdd: false,
                                                    canEdit: false
                                                },
                                                queryset: []
                                            },
                                            {
                                                width: 555,
                                                name: "lotacao_destino",
                                                fieldLabel: "Enviar p/ Lotação",
                                                xtype: "multiselectbox",
                                                toSearch: [],
                                                height: 200,
                                                allowBlank: true,
                                                validateOnBlur: true,
                                                blankText: "É necessário preencher este campo.",
                                                model: { name: "OrgaoGeral", pkg: "rh.models" },
                                                queryset: [],
                                                conf: {
                                                    canAdd: false,
                                                    canEdit: false
                                                },
                                                controller: this.father.geral == false ? "RHOrgaoGeralBuscaEspecial": "RHOrgaoGeral"
                                            },
                                        ]
                                    }
                                ]
                                })
                            ]
                        })
                    ]
                });
                this.form = this.formPanel.getComponent(0);
            }

            return this.formPanel;
        },

        show: function() {
            if(this.perm_envio){
                this.wnd = new Ext.Window({
                    title: "Movimentação em Lote",
                    closable: true,
                    modal: true,
                    'width': 720,
                    items: [ this.getFormPanel() ]
                });
                this.wnd.show();
            }
        }
    },

    /**
     * FORMULÁRIO PARA IMPRIMIR PROTOCOLO
     */
    toolkit.edocs.protocolo.ImprimirFormNew = function(father, codigo) {
       if(father != null) this.father = father;
       else throw new toolkit.widget.ExtNullPointerException("Bug: O objeto pai é requirido.");
        this.id = codigo;
        this.objects = {};
    },


    toolkit.edocs.protocolo.ImprimirFormNew.prototype = {

        commit: function() {
            var form = this.form.getForm();
            var values = form.getValues();
            values.movimentacao = this.id;
            var obj = toolkit.util.Ajax.request_json(
                "POST",
                toolkit.util.Normalize.controller_action(
                    "EDOCBox",
                    "validate",
                    ["imprimir"]
                ),
                values
            );
            if(!obj.success)
                alert(obj.msg);
            else {
                obj = toolkit.util.Ajax.request_json(
                    "POST",
                    toolkit.util.Normalize.controller_action(
                        "EDOCBox",
                        "commit",
                        ["imprimir"]
                    ),
                    values
                );
                if(!obj.result)
                    alert(obj.msg);
                else this.wnd.destroy();
            }
        },

        getFormPanel: function() {
            if(this.form == undefined) {
                this.formPanel = new Ext.Panel({
                        border: false,
                        buttonAlign: "right",
                        buttons: [
                            {
                                text: "Imprimir",
                                handler: this.commit,
                                scope: this
                            },
                            {
                                text: "Cancelar",
                                handler: function() { this.wnd.destroy(); },
                                scope: this
                            }
                        ],
                        items: [
                            this.form = new Ext.form.FormPanel({
                                border: false,
                                items: [
                                    new Ext.TabPanel({
                                        activeTab: 0,
                                        height: 100,
                                        border: false,
                                        items: [
                                            {
                                                xtype: "panel",
                                                layout: "form",
                                                title: "Informações",
                                                border: false,
                                                style: "margin: 5pt",
                                                defaults: { width: 370 },
                                                labelWidth: 120,
                                                items: [
                                                    {
                                                        allowBlank: false,
                                                        hiddenName: "impressora",
                                                        fieldLabel: "Impressora",
                                                        xtype: "combo",
                                                        displayField: "description",
                                                        valueField: "id",
                                                        store: new Ext.data.JsonStore({
                                                            root: "result",
                                                            url: toolkit.util.Normalize.controller_action(
                                                                "EDOCBox",
                                                                "get_store",
                                                                ["impressora"]
                                                            ),
                                                            fields: [ "id", "description"],
                                                            autoLoad: true
                                                        }),
                                                        triggerAction: "all",
                                                        mode: 'local'
                                                    },
                                                    {
                                                        fieldLabel: "Quantidade",
                                                        hiddenName: "quantidade",
                                                        xtype: "combo",
                                                        store: new Ext.data.SimpleStore({
                                                            fields: ["id", "desc"],
                                                            data: [['1', '1'], ['2', '2'],
                                                                    ['3', '3'], ['4', '4'],
                                                                    ['5', '5'], ['6', '6'],
                                                                    ['7', '7'], ['8', '8'],
                                                                    ['9', '9'], ['10', '10']]
                                                        }),
                                                        valueField: "id",
                                                        displayField: "desc",
                                                        mode: "local",
                                                        triggerAction: "all"
                                                    }
                                                ]
                                            },
                                        ]
                                    })
                                ]
                            })
                        ]
                    })
            }

            return this.formPanel;
        },

        show: function() {
            this.wnd = new Ext.Window({
                title: "Impressão de Etiqueta",
                closable: true,
                modal: true,
                width: 525,
                items: [ this.getFormPanel() ]
            });
            this.wnd.show();
        }
    }

    /**
     * FORMULÁRIO PARA VISUALIZAR PROTOCOLO
     */
    toolkit.edocs.protocolo.ProtocoloFormView = function(father, codigo, movimentacao, geral, caixa) {
        this.stores = { "movimentos": undefined }
        if(father != null) this.father = father;
        else throw new toolkit.widget.ExtNullPointerException("Bug: O objeto pai é requirido.");
        this.geral = geral;
        this.movimentacao = movimentacao;
        this.codigo = codigo;
        this.objects = {};
        this.caixa = caixa;
    },


    toolkit.edocs.protocolo.ProtocoloFormView.prototype = {

        stores: { "movimentos": undefined },

        quantidade_anexo: function(anexos){ return "Anexos("+anexos.length+")";},

        quantidade_referencia: function(referencia){ return "Referências("+referencia.length+")";},

        quantidade_referenciado_por: function(referencia_por){ return "Referenciado por("+referencia_por.length+")";},

        com_copia_para: function(com_copia_para){ return "Compartilhado com("+com_copia_para.length+")"; },

        show: function() {
            var tpl = new Ext.XTemplate(
                "<table class=\"property\">",
                    "<tr>",
                        "<td class=\"field\">Num. Protocolo :</td>",
                        "<td>{numero}</td>",
                    "</tr>",
                    "<tr>",
                        "<td class=\"field\">Num. Externo :</td>",
                        "<td>{protocolo_externo}</td>",
                    "</tr>",
                    "<tr>",
                        "<td class=\"field\">Chancela :</td>",
                        "<td class=\"value\">{chancela}</td>",
                    "</tr>",
                    "<tr>",
                        "<td class=\"field\">Tipo :</td>",
                        "<td class=\"value\">{tipo}</td>",
                    "</tr>",
                    "<tr>",
                        "<td class=\"field\">Assunto :</td>",
                        "<td class=\"value\">{assunto}</td>",
                    "</tr>",
                    "<tr>",
                        "<td class=\"field\">Protocolado por :</td>",
                        "<td class=\"value\">{origem}</td>",
                    "</tr>",
                    "<tr>",
                        "<td class=\"field\">Interessado :</td>",
                        "<td class=\"value\">{interessado}</td>",
                    "</tr>",
                    "<tr>",
                        "<td class=\"field\">Resumo :</td>",
                        "<td class=\"value\"></td>",
                    "</tr>",
                    "<tr>",
                        "<td colspan=\"2\" class=\"value\"><div style=\"height: 70px; width: 660px; overflow: auto; padding: 8px;\">{resumo}</div></td>",
                    "</tr>",
                "</table>"
            );

            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action(
                    "EDOCBox",
                    "view",
                    ["geral"]
                ),
                params: { codigo: this.codigo },
                method: 'POST',
                scope: this,
                success: function(request) {
                    var code = Ext.util.JSON.decode(request.responseText);
                    this.wnd = new Ext.Window({
                        title: "Visualização do Protocolo",
                        closable: true,
                        modal: true,
                        width: 700,
                        items: [
                            new Ext.Panel({
                                border: true,
                                bodyStyle: "border:none;border-bottom:1px solid #99bbe8",
                                html: tpl.apply(code)
                            }),
                            new Ext.TabPanel({
                                height: 190,
                                width: 685,
                                activeTab: 0,
                                tabPosition: "bottom",
                                border: false,
                                items: [
                                    new Ext.grid.GridPanel({
                                        showPreview: true, // custom property
                                        enableRowBody: true, // required to create a second, full-width row to show expanded Record data
                                        viewConfig:{
                                            getRowClass: function(record, rowIndex, rp, ds){ // rp = rowParams
                                              if(record.data.recebido=='') return 'rowRed';
                                              else if(record.data.recebido!='') return 'rowGreen';
                                              else return 'rowYellow';
                                            }
                                        },
                                        title: "Movimentações",
                                        tbar: [
                                            {
                                                text: "Ver Parecer",
                                                iconCls: true,
                                                icon: "/" + global.Context + "/static/engine/images/icons/athenas-0098.png",
                                                handler: function() {
                                                    if(this.wnd.getComponent(1).getComponent(0).getSelectionModel().getSelected()){
                                                        new toolkit.edocs.protocolo.ParecerFormView(this,
                                                            this.wnd.getComponent(1).getComponent(0).getSelectionModel().getSelected().get("movimentacao")).show();
                                                    }else alert("Para visualizar o parecer selecione uma movimentação abaixo.")
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
                                                if(this.wnd.getComponent(1).getComponent(0).getSelectionModel().getSelected()){
                                                    new toolkit.edocs.protocolo.ParecerFormView(this,
                                                        this.wnd.getComponent(1).getComponent(0).getSelectionModel().getSelected().get("movimentacao")).show();
                                                }
                                            }
                                        }
                                    }),
                                    new Ext.grid.GridPanel({
                                        tbar: [
                                            {
                                                text: "Download de anexo",
                                                iconCls: true,
                                                icon: "/" + global.Context + "/static/engine/images/icons/athenas-0082.png",
                                                handler: function() {
                                                 if(this.wnd.getComponent(1).getComponent(1).getSelectionModel().getSelected())
                                                    window.open(
                                                      this.wnd.getComponent(1).getComponent(1).getSelectionModel().getSelected().get("link"),"downloadFile"
                                                    );
                                                },
                                                scope: this
                                            }
                                        ],
                                        title: this.quantidade_anexo(code.anexos),
                                        sm: new Ext.grid.RowSelectionModel({ singleSelect: true }),
                                        store: new Ext.data.JsonStore({
                                            data: code.anexos,
                                            fields: ["nome","descricao", "link", "enviado_por"]
                                        }),
                                        cm: new Ext.grid.ColumnModel([
                                            {dataIndex: "nome",header: "Nome", width: 200},
                                            {dataIndex: "descricao",header: "Descrição", width: 250},
                                            {dataIndex: "enviado_por",header: "Enviado em", width: 410}
                                        ]),
                                        listeners: {
                                            scope: this,
                                            dblclick: function() {
                                                 if(this.wnd.getComponent(1).getComponent(1).getSelectionModel().getSelected())
                                                    window.open(
                                                        this.wnd.getComponent(1).getComponent(1).getSelectionModel().getSelected().get("link"),"downloadFile"
                                                    );
                                            }
                                        }
                                    }),
                                    new Ext.grid.GridPanel({
                                        title: this.quantidade_referencia(code.referencias),
                                        tbar: [
                                            {
                                                text: "Abrir Protocolo",
                                                iconCls: true,
                                                icon: "/" + global.Context + "/static/images/document-open.png",
                                                handler: function() {
                                                    if(this.wnd.getComponent(1).getComponent(2).getSelectionModel().getSelected()){
                                                        toolkit.edocs.protocolo.Box.prototype._openProtocoloFormView(
                                                            0,
                                                            this.wnd.getComponent(1).getComponent(2).getSelectionModel().getSelected().get("codigo"),
                                                            0
                                                        );
                                                    }else alert("Selecione uma movimentação abaixo.");
                                                },
                                                scope: this
                                            }
                                        ],
                                        store: new Ext.data.JsonStore({
                                            data: code.referencias,
                                            fields: ["codigo", "assunto", "resumo"]
                                        }),
                                        sm: new Ext.grid.RowSelectionModel({ singleSelect: true}),
                                        cm: new Ext.grid.ColumnModel([
                                            {dataIndex: "codigo",header: "Código", width: 150},
                                            {dataIndex: "assunto",header: "Assunto", width: 290},
                                            {dataIndex: "resumo",header: "Resumo", width: 420},
                                        ]),
                                        listeners: {
                                            scope: this,
                                            dblclick: function() {
                                            if(this.wnd.getComponent(1).getComponent(2).getSelectionModel().getSelected())
                                                toolkit.edocs.protocolo.Box.prototype._openProtocoloFormView(
                                                    0,
                                                    this.wnd.getComponent(1).getComponent(2).getSelectionModel().getSelected().get("codigo"),
                                                    0
                                                );
                                            }
                                        }
                                    }),
                                    new Ext.grid.GridPanel({
                                        title: this.quantidade_referenciado_por(code.referenciado_por),
                                        tbar: [
                                            {
                                                text: "Abrir Protocolo",
                                                iconCls: true,
                                                icon: "/" + global.Context + "/static/images/document-open.png",
                                                handler: function() {
                                                    if(this.wnd.getComponent(1).getComponent(3).getSelectionModel().getSelected()){
                                                        toolkit.edocs.protocolo.Box.prototype._openProtocoloFormView(
                                                            0,
                                                            this.wnd.getComponent(1).getComponent(3).getSelectionModel().getSelected().get("codigo"),
                                                            0
                                                        );
                                                    }else alert("Selecione uma movimentação abaixo.");
                                                },
                                                scope: this
                                            }
                                        ],
                                        store: new Ext.data.JsonStore({
                                            data: code.referenciado_por,
                                            fields: ["codigo", "assunto", "resumo"]
                                        }),
                                        sm: new Ext.grid.RowSelectionModel({ singleSelect: true }),
                                        cm: new Ext.grid.ColumnModel([
                                            {dataIndex: "codigo",header: "Código", width: 150},
                                            {dataIndex: "assunto",header: "Assunto", width: 290},
                                            {dataIndex: "resumo",header: "Resumo", width: 420},
                                        ]),
                                        listeners: {
                                            scope: this,
                                            dblclick: function() {
                                                if(this.wnd.getComponent(1).getComponent(3).getSelectionModel().getSelected())
                                                    toolkit.edocs.protocolo.Box.prototype._openProtocoloFormView(
                                                        0,
                                                        this.wnd.getComponent(1).getComponent(3).getSelectionModel().getSelected().get("codigo"),
                                                        0
                                                    );
                                            }
                                        }
                                    }),
                                    new Ext.grid.GridPanel({
                                        title: this.com_copia_para(code.com_copia_para),
                                        store: new Ext.data.JsonStore({
                                            data: code.com_copia_para,
                                            fields: ["codigo", "nome"]
                                        }),
                                        sm: new Ext.grid.RowSelectionModel({ singleSelect: true }),
                                        cm: new Ext.grid.ColumnModel([
                                            {dataIndex: "codigo",header: "Código", width: 150},
                                            {dataIndex: "nome",header: "Nome", width: 710}
                                        ])
                                    })
                                ]
                            })
                        ],
                        buttonAlign: "center",
                        buttons: this.getButtons()
                    });
                    this.wnd.show();
                },
                failure: function() { alert("Não foi possivel resgatar informações no servidor. Tente novamente mais tarde.");}
            });
        },

        receber: function(movs, stores){
            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action(
                    "EDOCBox",
                    "receber"
                ),
                params: {movimentacao: movs },
                scope: this,
                success: function(request) {
                    var code = Ext.util.JSON.decode(request.responseText);
                    if(!code.success) alert(code.msg);
                    else{
                        try{
                            if(stores["in"] != undefined) stores["in"].reload();
                            if(stores["out"] != undefined) stores["out"].reload();
                            if(stores["movimentos"] != undefined) stores["movimentos"].reload();
                        }catch(e){}
                    }
                },
                failure: function() { alert("Ocorreu um erro tentando receber o protocolo.");}
            })
        },

        marcar_nao_recebido: function(movs, stores){
            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action(
                    "EDOCBox",
                    "marcar_nao_recebido"
                ),
                params: {movimentacao: movs },
                scope: this,
                success: function(request) {
                    var code = Ext.util.JSON.decode(request.responseText);
                    if(!code.success) alert(code.msg);
                    else{
                        try{
                            if(stores["in"] != undefined) stores["in"].reload();
                            if(stores["out"] != undefined) stores["out"].reload();
                            if(stores["movimentos"] != undefined) stores["movimentos"].reload();
                        }catch(e){}
                    }
                },
                failure: function() { alert("Ocorreu um erro tentando receber o protocolo.");}
            })
        },

        getButtons: function(){
            var buttons = [];
            if(this.father.geral){
                buttons.push({
                    text: "Imprimir Etiqueta",
                    handler: function() { new toolkit.edocs.protocolo.ImprimirFormNew( this, this.codigo).show(); },
                    scope: this
                });
            }
            if(this.caixa == 1){
                buttons.push({
                    text: "Movimentar",
                    handler: function() {
                        var mov = new toolkit.edocs.protocolo.MovFormNew( this.father,this.codigo,this.movimentacao);
                        mov.show();
                    },
                    scope: this
                });
                buttons.push({
                    text: "Receber",
                    scope: this,
                    handler: function() {
                        var movs = [this.movimentacao];
                        this.receber(movs, this.father.stores);
                    }
                });
            }
            buttons.push({
                text: "Fechar",
                handler: function() { this.wnd.destroy();},
                scope: this
            });
            return buttons;
        },

        getMovimentacoesStore: function(){
            if(this.stores["movimentos"] == undefined) {
                this.stores["movimentos"] = new Ext.data.JsonStore({
                    root: "result",
                    url: toolkit.util.Normalize.controller_action(
                        "EDOCBox",
                        "view",
                        ["movimentos"]
                    ),
                    totalProperty: "totalRows",
                    fields: ["movimentacao","encaminhado_por", "encaminhado","encaminhado_para","recebido","recebido_por"],
                    baseParams: { movimentacao: this.movimentacao, codigo: this.codigo}
                });
                this.stores["movimentos"].load({ params:{ start: 0, limit: 10 }});
            }
            this.father.stores["movimentos"] = this.stores["movimentos"];
            return this.stores["movimentos"];
        }
    }

    /**
     * FORMULÁRIO PARA VISUALIZAR PARECER
     */
    toolkit.edocs.protocolo.ParecerFormView = function(father,movimentacao) {
        if(father != null) this.father = father;
        else throw new toolkit.widget.ExtNullPointerException("Bug: O objeto pai é requirido.");
        this.movimentacao = movimentacao;
        this.objects = {};
    },


    toolkit.edocs.protocolo.ParecerFormView.prototype = {

        show: function() {
            var tpl = new Ext.XTemplate(
                "<table class=\"property\">",
                    "<tr>",
                        "<td><div style=\"height: 300px; width: 650px; overflow: auto; padding: 8px;\">{parecer}</div></td>",
                    "</tr>",
                "</table>"
            );

            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action(
                    "EDOCBox",
                    "get_parecer"
                ),
                params: { movimentacao: this.movimentacao },
                method: 'POST',
                scope: this,
                success: function(request) {
                    var code = Ext.util.JSON.decode(request.responseText);
                    this.wnd = new Ext.Window({
                        title: "Visualização do Parecer",
                        closable: true,
                        modal: true,
                        width: 600,
                        items: [
                            new Ext.Panel({
                                border: true,
                                bodyStyle: "border:none;border-bottom:1px solid #99bbe8",
                                html: tpl.apply(code)
                            }),
                        ],
                        buttonAlign: "center",
                        buttons: [
                            {
                                text: "Fechar",
                                handler: function() { this.wnd.destroy(); },
                                scope: this
                            }
                        ]
                    });
                    this.wnd.show();
                },
                failure: function() { alert("Não foi possivel resgatar informações no servidor. Tente novamente mais tarde."); }
            });
        }
    }

    /**
     * FORMULÁRIO CONFIGURAÇÕES
     */

    toolkit.edocs.protocolo.ConfigFormNew = function() {
        this.conf_values = this.getConfValues();
    },

    toolkit.edocs.protocolo.ConfigFormNew.prototype = {

        commit: function() {
            var form = this.form.getForm();
            var values = form.getValues();
            var obj = toolkit.util.Ajax.request_json(
                "POST",
                toolkit.util.Normalize.controller_action(
                    "EDOCBox",
                    "validate",
                    ["new_conf"]
                ),
                values
            );

            if(!obj.result) {
                for(var i in obj.errors) {
                    if(!isNaN(i)) {
                        var error = obj.errors[i];
                        var field = form.findField(error.field);
                        if(field) field.markInvalid();
                    }
                }
            }else {
                obj = toolkit.util.Ajax.request_json(
                    "POST",
                    toolkit.util.Normalize.controller_action(
                        "EDOCBox",
                        "commit",
                        ["new_conf"]
                    ),
                    values
                );
                if(!obj.result) alert(obj.message);
                else this.wnd.destroy();
            }
        },

        getFormPanel: function() {
            if(this.form == undefined) {
                this.formPanel = new Ext.Panel({
                    border: false,
                    buttonAlign: "right",
                    buttons: [
                        {
                            text: "Salvar",
                            handler: this.commit,
                            scope: this
                        },
                        {
                            text: "Cancelar",
                            handler: function() { this.wnd.destroy(); },
                            scope: this
                        }
                    ],
                    items: [
                        {
                            xtype: "form",
                            border: false,
                            style: "margin: 5pt",
                            defaults: { width: 385 },
                            labelWidth: 120,
                            items: [
                                  {
                                    name: "pessoa",
                                    fieldLabel: "Pessoa",
                                    xtype: "multiselectbox",
                                    toSearch: [],
                                    allowBlank: true,
                                    validateOnBlur: true,
                                    value: this.conf_values.pessoa,
                                    blankText: "É necessário preencher este campo.",
                                    model: { name: "PessoaFisica", pkg: "rh.models" },
                                    conf: {
                                        canAdd: false,
                                        canEdit: false
                                    },
                                    queryset: []
                                 },
                                  {
                                    name: "permissao",
                                    fieldLabel: "Permissões",
                                    xtype: "multiselectbox",
                                    toSearch: [],
                                    allowBlank: true,
                                    validateOnBlur: true,
                                    value: this.conf_values.permissao,
                                    blankText: "É necessário preencher este campo.",
                                    model: { name: "PermissaoEdoc", pkg: "protocolo.models" },
                                    queryset: []
                                 },
                            ]
                        }
                    ]
                });
                this.form = this.formPanel.getComponent(0);
            }
            return this.formPanel;
        },

        getConfValues: function(){
            var obj = toolkit.util.Ajax.request_json(
                "POST",
                toolkit.util.Normalize.controller_action(
                    "EDOCBox",
                    "get_conf_values"
                )
            );
            return obj;
        },

        show: function() {
            this.wnd = new Ext.Window({
                title: "Configuração",
                closable: true,
                modal: true,
                items: [ this.getFormPanel() ]
            });
            this.wnd.show();
        }
    }
}
