Ext.ns('toolkit.rh.gestorafastamento');

Ext.apply(toolkit.rh.gestorafastamento,{
    GestorAfastamento: Ext.extend(Ext.TabPanel,{
        constructor: function(cfg) {
            var cf = {
                title: 'Afastamentos, Licenças e Ausências',
                activeTab: 0,
                closable: true,
                tabPosition: 'top',
                border: false,
                autoRender: true,
                items:[
                    new toolkit.rh.gestorafastamento.AfastamentoGridPanel({departamento: cfg.departamento}),
                    new toolkit.rh.gestorafastamento.SubstituicaoGeralGridPanel(),
                    new toolkit.rh.gestorafastamento.InativacaoGeralGridPanel()
                ]
            };
            toolkit.rh.gestorafastamento.GestorAfastamento.superclass.constructor.call(this, cf);
            var active = toolkit.Application.tabspace.getActiveTab();
            toolkit.Application.tabspace.remove(active);
            toolkit.Application.tabspace.add(this);
        }
    }),

    SubstituicaoGeralGridPanel: Ext.extend(toolkit.rh.gestorafastamento.utils.SubstituicaoGridPanel,{
        constructor: function(args) {
            var cf = {
                title: 'Substituições',
                height: 600,
                searchable: true,
                region: 'center',
                autoExpandColumn: 'cargo',
                toSearch: [
                    {dataIndex: 'cargo', header: 'Servidor', sortable: false, width: 250}
                ],
                pageSize: 10,
                controller: 'RHMovimentacaoSubstituicao',
                listeners: {
                    scope: this,
                    dblclick: function() {
                        alert('Utilize a aba Gestor de Afastamentos para modificar uma substituição!');
                    },
                    beforeshow: function(component){ this.getStore().load(); }
                },
                method_list: 'list_substitute'
            };
            toolkit.rh.gestorafastamento.SubstituicaoGeralGridPanel.superclass.constructor.call(this, cf);
        },

        getColumnModel: function(){
            if(!this.colModelGridPanel){
                this.colModelGridPanel = new Ext.grid.ColumnModel({
                    columns: [
                        {header: "Código", sortable: false, dataIndex: "pk", key: "pk", id: "pk", width: 50},
                        {header: "Cargo", sortable: false, dataIndex: "cargo", key: "cargo", id: "cargo", width: 225},
                        {header: "Substituto", sortable: false, dataIndex: "substituto", key: "substituto", id: "substituto", width: 200},
                        {header: "Situação", sortable: true, dataIndex: "situacao", key: "situacao", width: 70},
                        {header: "Início", sortable: true, dataIndex: "data_inicio", key: "data_inicio", width: 80},
                        {header: "Prevista", sortable: true, dataIndex: "data_prevista", key: "data_prevista", width: 80},
                        {header: "Fim", sortable: true, dataIndex: "data_fim", key: "data_fim", width: 80}
                    ]
                });
            }
            return this.colModelGridPanel;
        },

        getToolbar: function(){
            return toolkit.rh.gestorafastamento.utils.SubstituicaoGridPanel.superclass.getToolbar.call(this, {});
        },

        _getToolbar: function(){
            var tbar = toolkit.rh.utils.CustomGridPanel.superclass.getToolbar.call(this, {});
            tbar.insertButton(1, {
                    text:'Novo',
                    icon: "/" + global.Context + "/static/images/add.png",
                    menu: toolkit.rh.gestorafastamento.utils.MenuSubstituicaoGeral({
                        membro: {scope: this, handler: function(){
                                new toolkit.rh.gestorafastamento.utils.WindowFormSubstituicaoMembro({
                                    "substituicao": undefined,
                                    "afastamento": undefined,
                                    "servidor": undefined,
                                    "store_call_back": this.getStore()
                                }).show();
                            }
                        },
                        servidor: {scope: this, handler: function(){
                                new toolkit.rh.gestorafastamento.utils.ExtCrudCall({
                                    controller: 'RHMovimentacaoSubstituicao',
                                    store: this.getStore()
                                }).call();
                            }
                        }
                    })
                });
            tbar.insertButton(2, '-');
            tbar.insertButton(3, {
                    text: 'Editar',
                    iconCls: true,
                    icon: "/" + global.Context + "/static/images/edit.png",
                    handler: function() {
                        this.servidor_tipo = this.getSelectionModel().getSelected().get("tipo");
                        this.callWindowFormSubstituicao(
                            'EDIT',
                            this.getSelectionModel().getSelected().get("pk"));
                    },
                    scope: this
                });
            tbar.insertButton(4, '-');
            tbar.insertButton(5, {
                    text: 'Apagar',
                    iconCls: true,
                    icon: "/" + global.Context + "/static/images/delete.png",
                    handler: function() {
                        if(this.getSelectionModel().getSelected()){
                            var id = this.getSelectionModel().getSelected().get("pk");
                            var fn = function(bnt, text, opts) {
                                if(bnt == "yes") {
                                    var obj = toolkit.util.Ajax.request_json(
                                        "POST",
                                        toolkit.util.Normalize.controller_action(
                                            this.getSelectionModel().getSelected().get("tipo") == "servidor" ? "RHMovimentacaoSubstituicao" : "RHMovimentacaoSubstituicaoMembro",
                                            "commit",
                                            ["DELETE", id, 0])
                                    );
                                    var store = this.getStore();
                                    setTimeout(function() { store.load(); }, 100);
                                }
                                else if(bnt == "no") {
                                    if(this.getSelectionModel().getSelected().get("tipo") == "servidor"){
                                        this.chamarExtCrud({
                                            controller: "RHMovimentacaoSubstituicao",
                                            pk: this.getSelectionModel().getSelected().get("pk"),
                                            tipo: 'DELETE',
                                            fields: [{ name: "servidor", enabled: false }]
                                        });
                                    }else{
                                        new toolkit.rh.gestorafastamento.utils.WindowFormSubstituicaoMembro({
                                            "substituicao": this.getSelectionModel().getSelected().get("pk"),
                                            "afastamento": undefined,
                                            "servidor": undefined,
                                            "store_call_back": this.getStore()
                                        }).show();
                                    }
                                }
                                else {
                                    Ext.MessageBox.show({
                                        title: "Sistema Administrativo",
                                        msg : "A ação de remoção foi cancelada.",
                                        buttons: Ext.MessageBox.OK,
                                        icon: Ext.MessageBox.INFO
                                    });
                                }

                            };

                            Ext.MessageBox.show({
                                title: "ManagerNetWork",
                                msg : "Tem certeza que deseja remover o item com id " + id + ", \n\
                                    caso não tenha certeza clique em <b>Não</b> para visualizar os dados. \n\
                                    <b>TODAS substituições</b> agendadas para este afastamento serão apagadas!",
                                fn : fn,
                                scope: this,
                                buttons: Ext.MessageBox.YESNOCANCEL,
                                icon: Ext.MessageBox.QUESTION
                            });
                        }else{ alert('Escolha uma Substituição!');}
                    },
                    scope: this
                });
            tbar.insertButton(6, '-');
            return tbar;
        }
    }),

    InativacaoGeralGridPanel: Ext.extend(toolkit.rh.utils.CustomGridPanel,{
        constructor: function(args) {
            var cf = {
                title: 'Inativações',
                controller: 'RHInativacaoCargoMembro',
                searchable: true,
                region: 'center',
                readerFields: [
                    {name: 'pk'},
                    {name: 'posse'},
                    {name: 'data_inicio'},
                    {name: 'data_fim'},
                    {name: 'data_prevista'},
                    {name: 'situacao'}
                ],
                listeners: {
                    scope: this,
                    dblclick: function() {
                        this.chamarExtCrud({
                            controller: this.getSelectionModel().getSelected().get("controller"),
                            pk: this.getSelectionModel().getSelected().get("pk"),
                            tipo: 'EDIT',
                            fields: [{ name: "servidor", enabled: false }]
                        });
                    },
                    beforeshow: function(component){ this.getStore().reload(); }
                }
            };
            toolkit.rh.gestorafastamento.InativacaoGeralGridPanel.superclass.constructor.call(this, cf);
        },

        getColumnModel: function(){
            if(!this.colModelGridPanel){
                this.colModelGridPanel = new Ext.grid.ColumnModel({
                    columns: [
                        {header: "Código", sortable: false, dataIndex: "pk", key: "pk", id: "pk", width: 50},
                        {header: "Cargo", sortable: false, dataIndex: "posse", key: "posse", id: "posse", width: 520},
                        {header: "Situação", sortable: false, dataIndex: "situacao", key: "situacao", id: "situacao", width: 120},
                        {header: "Início", sortable: true, dataIndex: "data_inicio", key: "data_inicio", width: 85},
                        {header: "Prevista", sortable: true, dataIndex: "data_prevista", key: "data_prevista", width: 85},
                        {header: "Fim", sortable: true, dataIndex: "data_fim", key: "data_fim", width: 85}
                    ]
                });
            }
            return this.colModelGridPanel;
        }
    }),

    AfastamentoGridPanel: Ext.extend(toolkit.rh.utils.CustomGridPanel,{
        constructor: function(args) {
            this.departamento = args.departamento;
            var cf = {
                id: 'afastamentogridpanel',
                title: 'Gestor de Afastamentos',
                searchable: true,
                region: 'center',
                pageSize: 10,
                controller: 'AFAGestorAfastamento',
                scope: this,
                // items: [
                //     new Ext.Panel({
                //         // layout: 'fit',
                //         border: false,
                //         tbar: this.getSecondToolBar()})
                // ],
                readerFields: [
                    {name: 'pk'},
                    {name: 'data_inicio'},
                    {name: 'data_fim'},
                    {name: 'data_prevista'},
                    {name: 'servidor'},
                    {name: 'servidor_matricula'},
                    {name: 'servidor_pk'},
                    {name: 'motivo'},
                    {name: 'status'},
                    {name: 'controller'},
                    {name: 'anotacao'},
                    {name: 'anotacao_class'},
                    {name: 'agendamento'},
                    {name: 'alteracao'},
                    {name: 'servidor_tipo'},
                    {name: 'created_by'},
                    {name: 'created_at'},
                    {name: 'modified_by'},
                    {name: 'modified_at'},
                ],
                listeners: {
                    scope: this,
                    dblclick: function() {
                        if(this.getSelectionModel().getSelected().get("controller") == "ExtCrudGeneric" ||
                            // this.getSelectionModel().getSelected().get("controller") == "AFAViagem" ||
                            this.getSelectionModel().getSelected().get("controller") == "AFAFeriasAfastamento"){
                            alert(this.getSelectionModel().getSelected().get("motivo") + ' só pode ser alterado através de sua origem!');
                            return true;
                        }
                        this.chamarExtCrud({
                            controller: this.getSelectionModel().getSelected().get("controller"),
                            pk: this.getSelectionModel().getSelected().get("pk"),
                            tipo: 'EDIT',
                            fields: [{ name: "servidor", enabled: false }]
                        });
                    },
                    beforeshow: function(component){ this.getStore().reload(); }
                }
            };
            toolkit.rh.gestorafastamento.AfastamentoGridPanel.superclass.constructor.call(this, cf);
        },

        getStore: function(){
            if(!this.storeGridPanel){
                    tipoServidorValor = ''
                    if(this.departamento == 'expediente')
                        tipoServidorValor = 'M'
                    this.storeGridPanel = new Ext.data.Store({
                        id: 'store',
                        autoLoad: false,
                        proxy: this.getProxy(),
                        reader: this.getReader(),
                        writer: this.getWriter(),
                        autoSave: true,
                        baseParams: {
                            tipoServidor: tipoServidorValor,
                            onlyAfastamento: true,
                            onlyAusencia: true,
                            onlyFerias: true,
                            onlyLicenca: true,
                            onlyRecesso: true,
                            onlyFolgaCompensacao: true,
                            onlyFolgaEleitoral: true,
                            onlyFolgaAniversario: true,
                            onlyAtuacaoGrupoTrabalho: true,
                            onlyDesempenhoFuncao: true,
                            onlyPlantao: true,
                            onlyViagem: true,
                            onlyAtivo: true,
                            onlyAgendado: true,
                            onlyCancelado: this.departamento == 'expediente' ? true : false,
                            onlyEncerrado: this.departamento == 'expediente' ? true : false,
                            onlyInterruption: true,
                            onlyRequest: true,
                            onlyRevocation: true,
                            onlySuspension: true,
                            onlyComparecimentoJuizo: true,
                            onlyCandidatura: true,
                            onlyCompeticao: true,
                            onlyCursoFormacaoConcurso: true,
                            onlyDeslocamento: true,
                            onlyJusticaEleitoral: true,
                            onlyEstudar: true,
                            onlyExercicioMandato: true,
                            onlyMissao: true,
                            onlyPrisao: true,
                            onlyServirOutroOrgao: true,
                            onlyServirJuri: true,
                            onlySuspensao: true,
                            onlySindicanciaAdm: true,
                            onlyTreinamento: true,
                            onlyAfastamentoConjuge: true,
                            onlyAtividadePolitica: true,
                            onlyCapacitacao: true,
                            onlyMandatoClassista: true,
                            onlyDoencaFamilia: true,
                            onlyMaternidade: true,
                            onlyServicoMilitar: true,
                            onlyTratamento3dias: true,
                            onlyTratamento30dias: true,
                            onlyTratamentoJuntaMedica: true,
                            onlyInteresseParticular: true,
                            onlyTutoria: true,
                            onlyAlistamentoEleitor: true,
                            onlyCasamento: true,
                            onlyDoacaoSangue: true,
                            onlyFalecimento: true,
                            onlyConclusaoTcc: true,
                            onlyNascimento: true,
                            onlyRecessoForense: true,
                        }
                    });
                if(this.cf.readerFields[0].name == '_pk')
                    this.storeGridPanel.loadData(
                        {"totalRows": 11, "result": [
                            {'_pk':'1', '_nome':'Fulano'},{'_pk':'2', '_nome':'Cicrano'}]});
            }
            return this.storeGridPanel;
        },

        getMainMenu: function(){
            if(!this.gridMainMenu){
                this.gridMainMenu = toolkit.rh.gestorafastamento.utils.MenuSubstituicao({
                    membro: {scope: this, handler: this.callSubstituicoesInativacoes},
                    servidor: {scope: this, handler: function(){
                            if(this.getSelectionModel().getSelected().get("status") == 'CANCELADO')
                                alert("Afastamento CANCELADO!");
                            else{
                                new toolkit.rh.gestorafastamento.utils.ExtCrudCall({
                                    controller: 'RHMovimentacaoSubstituicao',
                                    store: this.getStore(),
                                    fields: [
                                        { name: 'afastamento', enabled: false, value: this.getSelectionModel().getSelected().get("pk") }]
                                }).call();
                            }
                        }
                    }
                });
                return this.gridMainMenu;
            }
        },

        getMenuNovo: function(){
            if(!this.gridMenuNovo){
                this.gridMenuNovo= new Ext.menu.Menu({
                    id: 'menuNovo',
                    split: true,
                    defaultStyle: 'splitbutton',
                    style: { overflow: 'visible' },
                    scope: this,
                    items: [
                        {
                            text:'Novo',
                            iconCls: true,
                            icon: "/" + global.Context + "/static/images/add.png",
                            menu: [
                                toolkit.rh.gestorafastamento.utils.MenuAfastamento({scope: this}),
                                toolkit.rh.gestorafastamento.utils.MenuLicenca({scope: this}),
                                toolkit.rh.gestorafastamento.utils.MenuAusencia({scope: this}),
                                {
                                    text: 'Usufrutos',
                                    menu: [
                                        new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                                            text: 'Folga Aniversário',
                                            controller: 'AFAFolgaAniversario',
                                            scope: this
                                        }),
                                        new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                                            text: 'Folga Compensação',
                                            controller: 'AFAFolgaCompensacao',
                                            scope: this
                                        }),
                                        new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                                            text: 'Folga Eleitoral',
                                            controller: 'AFAFolgaEleitoral',
                                            scope: this
                                        }),
                                        new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                                            text: 'Plantão de Feriado',
                                            controller: 'AFAPlantao',
                                            scope: this
                                        }),
                                        new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                                            text: 'Recesso Natalino',
                                            controller: 'AFARecesso',
                                            scope: this
                                        })
                                    ]
                                },
                                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                                    text: 'Atuação em Grupo de Trabalho',
                                    controller: 'AFAAtuacaoGrupoTrabalho',
                                    scope: this
                                }),
                                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                                    text: 'Desempenho de Função',
                                    controller: 'AFADesempenhoFuncao',
                                    scope: this
                                })
                            ]
                        },
                        {
                            text: 'Editar',
                            iconCls: true,
                            icon: "/" + global.Context + "/static/images/edit.png",
                            handler: function() {
                                if(this.getSelectionModel().getSelected().get("controller") == "ExtCrudGeneric" ||
                                    // this.getSelectionModel().getSelected().get("controller") == "AFAViagem" ||
                                    this.getSelectionModel().getSelected().get("controller") == "AFAFeriasAfastamento"){
                                    alert(this.getSelectionModel().getSelected().get("motivo") + ' só pode ser alterado através de sua origem!');
                                    return true;
                                }
                                this.chamarExtCrud({
                                    controller: this.getSelectionModel().getSelected().get("controller"),
                                    pk: this.getSelectionModel().getSelected().get("pk"),
                                    tipo: 'EDIT',
                                    fields: [{ name: "servidor", enabled: false }]
                                });
                            },
                            scope: this
                        },
                        {
                            text:'Apagar',
                            iconCls: true,
                            icon: "/" + global.Context + "/static/images/delete.png",
                            scope: this,
                            handler: function() {
                                if(this.getSelectionModel().getSelected()){
                                    var id = this.getSelectionModel().getSelected().get("pk");
                                    var fn = function(bnt, text, opts) {

                                        if(bnt == "yes") {
                                            var obj = toolkit.util.Ajax.request_json(
                                                "POST",
                                                toolkit.util.Normalize.controller_action(
                                                    this.getSelectionModel().getSelected().get("controller"),
                                                    "commit",
                                                    ["DELETE", id, 0])
                                            );
                                            var store = this.getStore();
                                            setTimeout(function() { store.load(); }, 100);
                                        }
                                        else if(bnt == "no") {
                                            this.chamarExtCrud({
                                                controller: this.getSelectionModel().getSelected().get("controller"),
                                                pk: this.getSelectionModel().getSelected().get("pk"),
                                                tipo: 'DELETE',
                                                fields: [{ name: "servidor", enabled: false }]
                                            });
                                        }
                                        else {
                                            Ext.MessageBox.show({
                                                title: "Sistema Administrativo",
                                                msg : "A ação de remoção foi cancelada.",
                                                buttons: Ext.MessageBox.OK,
                                                icon: Ext.MessageBox.INFO
                                            });
                                        }

                                    };

                                    Ext.MessageBox.show({
                                        title: "ManagerNetWork",
                                        msg : "Tem certeza que deseja remover o item com id " + id + ", \n\
                                            caso não tenha certeza clique em <b>Não</b> para visualizar os dados. \n\
                                            <b>TODAS substituições</b> agendadas para este afastamento serão apagadas!",
                                        fn : fn,
                                        scope: this,
                                        buttons: Ext.MessageBox.YESNOCANCEL,
                                        icon: Ext.MessageBox.QUESTION
                                    });
                                }else{ alert('Escolha um Afastamento!');}
                            }
                        },
                        {
                            text: 'Anotação',
                            iconCls: true,
                            icon: "/" + global.Context + "/static/engine/images/icons/athenas-0333.png",
                            handler: function() {
                                if(this.getSelectionModel().getSelected().get("anotacao")){
                                    new toolkit.rh.utils.ExtCrudCall({
                                        controller: this.getSelectionModel().getSelected().get("anotacao_class"),
                                        pk: this.getSelectionModel().getSelected().get("anotacao"),
                                        tipo: 'EDIT',
                                        fields: [],
                                        store: this.getStore()
                                    }).call();
                                }else{ alert('Este afastamento não possui anotação!');}
                            },
                            scope: this
                        },
                        // '-',
                    ]
                });
                return this.gridMenuNovo;
            }
        },

        getColumnModel: function(){
            if(!this.colModelGridPanel){
                this.colModelGridPanel = new Ext.grid.ColumnModel({
                    columns: [
                        {header: "Código", sortable: true, dataIndex: "pk", key: "pk", id: "pk", width: 50},
                        // {header: "Status", sortable: true, dataIndex: "agendamento", key: "agendamento", id: "agendamento", width: 50},
                        {
                            header: "Status",
                            dataIndex: "agendamento",
                            key: "agendamento",
                            id: "agendamento",
                            align: "center",
                            width: 50,
                            renderer: function(value){
                                var tpl = new Ext.XTemplate(
                                    "<div>",
                                        "<tpl for=\"icons\">",
                                        "<img style=\"margin-right:4px;width:12px;height:12px;)\" src=\"{url}\" title=\"{title}\"/>",
                                        "</tpl>",
                                    "</div>"
                                );
                                return tpl.apply({
                                    "icons": {
                                        url: toolkit.util.Normalize.controller_action(
                                            "static/engine/images", "icons") + (
                                                value.existe_agendamento == true ? "athenas-0394.png": "athenas-0606.png"),
                                        title: value.title
                                    }
                                });
                            }
                        },
                        {header: "Servidor", sortable: true, dataIndex: "servidor", key: "servidor", id: "servidor", width: 260},
                        {header: "Motivo", sortable: true, dataIndex: "motivo", key: "motivo", id: "motivo", width: 240},
                        {header: "Situação", sortable: true, dataIndex: "status", key: "status", id: "status", width: 80, align: "center"},
                        {header: "Tipo de alteração", sortable: true, dataIndex: "alteracao", key: "alteracao", id: "alteracao", width: 100},
                        {header: "Início", sortable: true, dataIndex: "data_inicio", key: "data_inicio", width: 80},
                        {header: "Prevista", sortable: true, dataIndex: "data_prevista", key: "data_prevista", width: 80},
                        {header: "Fim", sortable: true, dataIndex: "data_fim", key: "data_fim", width: 85},
                        {header: "Criado por", sortable: true, dataIndex: "created_by", key: "created_by", width: 105},
                        {header: "Criado em", sortable: true, dataIndex: "created_at", key: "created_at", width: 105},
                        {header: "Modificado por", sortable: true, dataIndex: "modified_by", key: "modified_by", width: 105},
                        {header: "Modificação em", sortable: true, dataIndex: "modified_at", key: "modified_at", width: 105},
                    ]
                });
            }
            return this.colModelGridPanel;
        },

        setFilter: function() {
            var store = this.getStore();
            var fields = [];

            if (this.fieldsToSearch.menu){
                this.fieldsToSearch.menu.items.each(
                    function(item) {
                        if (item.checked)
                            fields.push(item.dataIndex);
                    });
            }

            var keyword = this.findText.getValue();

            if (keyword != undefined && keyword != '') {
                store.baseParams.keyword = keyword;
                if (fields.length > 0) store.baseParams.toSearch = fields;
            }
            else {
                store.baseParams.keyword = undefined;
                store.baseParams.toSearch = undefined;
            }
            var dataInicio = Ext.util.Format.date(this.dataInicioFind.getValue());
            var dataFim = Ext.util.Format.date(this.dataFimFind.getValue());
            if (dataInicio != undefined && dataInicio != '')
                store.baseParams.dataInicio = dataInicio;
            else
                store.baseParams.dataInicio = undefined;
            if (dataFim != undefined && dataFim != '')
                store.baseParams.dataFim = dataFim;
            else
                store.baseParams.dataFim = undefined;

            store.baseParams.checkAlteracao = this.checkAlteracao.checked;
            store.baseParams.onlyAtivo = this.checkOnlyAtivo.checked;
            store.baseParams.onlyAgendado = this.checkOnlyAgendado.checked;
            store.baseParams.onlyCancelado = this.checkOnlyCancelado.checked;
            store.baseParams.onlyEncerrado = this.checkOnlyEncerrado.checked;

            store.baseParams.onlyAfastamento = this.checkOnlyAfastamento.checked;
            store.baseParams.onlyAtuacaoGrupoTrabalho = this.checkOnlyAtuacaoGrupoTrabalho.checked;
            store.baseParams.onlyAusencia = this.checkOnlyAusencia.checked;
            store.baseParams.onlyFerias = this.checkOnlyFerias.checked;
            store.baseParams.onlyFolgaCompensacao = this.checkOnlyFolgaCompensacao.checked;
            store.baseParams.onlyFolgaEleitoral = this.checkOnlyFolgaEleitoral.checked;
            store.baseParams.onlyFolgaAniversario = this.checkOnlyFolgaAniversario.checked;
            store.baseParams.onlyDesempenhoFuncao = this.checkOnlyDesempenhoFuncao.checked;
            store.baseParams.onlyLicenca = this.checkOnlyLicenca.checked;
            store.baseParams.onlyPlantao = this.checkOnlyPlantao.checked;
            store.baseParams.onlyViagem = this.checkOnlyViagem.checked;
            store.baseParams.onlyRecesso = this.checkOnlyRecesso.checked;

            store.baseParams.onlyComparecimentoJuizo = this.checkOnlyComparecimentoJuizo.checked;
            store.baseParams.onlyCandidatura = this.checkOnlyCandidatura.checked;
            store.baseParams.onlyCompeticao = this.checkOnlyCompeticao.checked;
            store.baseParams.onlyCursoFormacaoConcurso = this.checkOnlyCursoFormacaoConcurso.checked;
            store.baseParams.onlyDeslocamento = this.checkOnlyDeslocamento.checked;
            store.baseParams.onlyJusticaEleitoral = this.checkOnlyJusticaEleitoral.checked;
            store.baseParams.onlyEstudar = this.checkOnlyEstudar.checked;
            store.baseParams.onlyExercicioMandato = this.checkOnlyExercicioMandato.checked;
            store.baseParams.onlyMissao = this.checkOnlyMissao.checked;
            store.baseParams.onlyPrisao = this.checkOnlyPrisao.checked;
            store.baseParams.onlyServirOutroOrgao = this.checkOnlyServirOutroOrgao.checked;
            store.baseParams.onlyServirJuri = this.checkOnlyServirJuri.checked;
            store.baseParams.onlySuspensao = this.checkOnlySuspensao.checked;
            store.baseParams.onlySindicanciaAdm = this.checkOnlySindicanciaAdm.checked;
            store.baseParams.onlyRecessoForense = this.checkOnlyRecessoForense.checked;
            store.baseParams.onlyTreinamento = this.checkOnlyTreinamento.checked;
            store.baseParams.onlyAfastamentoConjuge = this.checkOnlyAfastamentoConjuge.checked;
            store.baseParams.onlyAtividadePolitica = this.checkOnlyAtividadePolitica.checked;
            store.baseParams.onlyCapacitacao = this.checkOnlyCapacitacao.checked;
            store.baseParams.onlyMandatoClassista = this.checkOnlyMandatoClassista.checked;
            store.baseParams.onlyDoencaFamilia = this.checkOnlyDoencaFamilia.checked;
            store.baseParams.onlyMaternidade = this.checkOnlyMaternidade.checked;
            store.baseParams.onlyServicoMilitar = this.checkOnlyServicoMilitar.checked;
            store.baseParams.onlyTratamento3dias = this.checkOnlyTratamento3dias.checked;
            store.baseParams.onlyTratamento30dias = this.checkOnlyTratamento30dias.checked;
            store.baseParams.onlyTratamentoJuntaMedica = this.checkOnlyTratamentoJuntaMedica.checked;
            store.baseParams.onlyInteresseParticular = this.checkOnlyInteresseParticular.checked;
            store.baseParams.onlyTutoria = this.checkOnlyTutoria.checked;
            store.baseParams.onlyAlistamentoEleitor = this.checkOnlyAlistamentoEleitor.checked;
            store.baseParams.onlyCasamento = this.checkOnlyCasamento.checked;
            store.baseParams.onlyDoacaoSangue = this.checkOnlyDoacaoSangue.checked;
            store.baseParams.onlyFalecimento = this.checkOnlyFalecimento.checked;
            store.baseParams.onlyConclusaoTcc = this.checkOnlyConclusaoTcc.checked;
            store.baseParams.onlyNascimento = this.checkOnlyNascimento.checked;

            // store.baseParams.onlyCancellation = this.checkOnlyCancellation.checked;
            store.baseParams.onlyInterruption = this.checkOnlyInterruption.checked;
            store.baseParams.onlyRequest = this.checkOnlyRequest.checked;
            store.baseParams.onlyRevocation = this.checkOnlyRevocation.checked;
            store.baseParams.onlySuspension = this.checkOnlySuspension.checked;

            store.reload({params: {start: 0}});
        },

        markFilter: function(option){
            if(option == 'all'){
                // this.checkAlteracao.setValue(true);
                this.checkOnlyAtivo.setValue(true);
                this.checkOnlyAgendado.setValue(true);
                // this.checkOnlyCancelado.setValue(true);
                // this.checkOnlyEncerrado.setValue(true);

                this.checkOnlyAfastamento.setValue(true);
                this.checkOnlyAtuacaoGrupoTrabalho.setValue(true);
                this.checkOnlyAusencia.setValue(true);
                this.checkOnlyFerias.setValue(true);
                this.checkOnlyFolgaCompensacao.setValue(true);
                this.checkOnlyFolgaEleitoral.setValue(true);
                this.checkOnlyFolgaAniversario.setValue(true);
                this.checkOnlyDesempenhoFuncao.setValue(true);
                this.checkOnlyLicenca.setValue(true);
                this.checkOnlyPlantao.setValue(true);
                this.checkOnlyViagem.setValue(true);
                this.checkOnlyRecesso.setValue(true);

                this.checkOnlyComparecimentoJuizo.setValue(true);
                this.checkOnlyCandidatura.setValue(true);
                this.checkOnlyCompeticao.setValue(true);
                this.checkOnlyCursoFormacaoConcurso.setValue(true);
                this.checkOnlyDeslocamento.setValue(true);
                this.checkOnlyJusticaEleitoral.setValue(true);
                this.checkOnlyEstudar.setValue(true);
                this.checkOnlyExercicioMandato.setValue(true);
                this.checkOnlyMissao.setValue(true);
                this.checkOnlyPrisao.setValue(true);
                this.checkOnlyServirOutroOrgao.setValue(true);
                this.checkOnlyServirJuri.setValue(true);
                this.checkOnlySuspensao.setValue(true);
                this.checkOnlyTreinamento.setValue(true);
                this.checkOnlyAfastamentoConjuge.setValue(true);
                this.checkOnlyAtividadePolitica.setValue(true);
                this.checkOnlyCapacitacao.setValue(true);
                this.checkOnlyMandatoClassista.setValue(true);
                this.checkOnlyDoencaFamilia.setValue(true);
                this.checkOnlyMaternidade.setValue(true);
                this.checkOnlyServicoMilitar.setValue(true);
                this.checkOnlyTratamento3dias.setValue(true);
                this.checkOnlyTratamento30dias.setValue(true);
                this.checkOnlyTratamentoJuntaMedica.setValue(true);
                this.checkOnlyInteresseParticular.setValue(true);
                this.checkOnlyTutoria.setValue(true);
                this.checkOnlyAlistamentoEleitor.setValue(true);
                this.checkOnlyCasamento.setValue(true);
                this.checkOnlyDoacaoSangue.setValue(true);
                this.checkOnlyFalecimento.setValue(true);
                this.checkOnlyConclusaoTcc.setValue(true);
                this.checkOnlyNascimento.setValue(true);

                //this.checkOnlyCancellation.setValue(true);
                this.checkOnlyInterruption.setValue(true);
                this.checkOnlyRequest.setValue(true);
                this.checkOnlyRevocation.setValue(true);
                this.checkOnlySuspension.setValue(true);
            }else{
                this.checkAlteracao.setValue(false);
                // this.checkOnlyAtivo.setValue(false);
                // this.checkOnlyAgendado.setValue(false);
                // this.checkOnlyCancelado.setValue(false);
                // this.checkOnlyEncerrado.setValue(false);

                this.checkOnlyAfastamento.setValue(false);
                this.checkOnlyAtuacaoGrupoTrabalho.setValue(false);
                this.checkOnlyAusencia.setValue(false);
                this.checkOnlyFerias.setValue(false);
                this.checkOnlyFolgaCompensacao.setValue(false);
                this.checkOnlyFolgaEleitoral.setValue(false);
                this.checkOnlyFolgaAniversario.setValue(false);
                this.checkOnlyDesempenhoFuncao.setValue(false);
                this.checkOnlyLicenca.setValue(false);
                this.checkOnlyPlantao.setValue(false);
                this.checkOnlyViagem.setValue(false);
                this.checkOnlyRecesso.setValue(false);

                this.checkOnlyComparecimentoJuizo.setValue(false);
                this.checkOnlyCandidatura.setValue(true);
                this.checkOnlyCompeticao.setValue(false);
                this.checkOnlyCursoFormacaoConcurso.setValue(false);
                this.checkOnlyDeslocamento.setValue(false);
                this.checkOnlyJusticaEleitoral.setValue(false);
                this.checkOnlyEstudar.setValue(false);
                this.checkOnlyExercicioMandato.setValue(false);
                this.checkOnlyMissao.setValue(false);
                this.checkOnlyPrisao.setValue(false);
                this.checkOnlyServirOutroOrgao.setValue(false);
                this.checkOnlyServirJuri.setValue(false);
                this.checkOnlySuspensao.setValue(false);
                this.checkOnlyTreinamento.setValue(false);
                this.checkOnlyAfastamentoConjuge.setValue(false);
                this.checkOnlyAtividadePolitica.setValue(false);
                this.checkOnlyCapacitacao.setValue(false);
                this.checkOnlyMandatoClassista.setValue(false);
                this.checkOnlyDoencaFamilia.setValue(false);
                this.checkOnlyMaternidade.setValue(false);
                this.checkOnlyServicoMilitar.setValue(false);
                this.checkOnlyTratamento3dias.setValue(false);
                this.checkOnlyTratamento30dias.setValue(false);
                this.checkOnlyTratamentoJuntaMedica.setValue(false);
                this.checkOnlyInteresseParticular.setValue(false);
                this.checkOnlyTutoria.setValue(false);
                this.checkOnlyAlistamentoEleitor.setValue(false);
                this.checkOnlyCasamento.setValue(false);
                this.checkOnlyDoacaoSangue.setValue(false);
                this.checkOnlyFalecimento.setValue(false);
                this.checkOnlyConclusaoTcc.setValue(false);
                this.checkOnlyNascimento.setValue(false);

                //this.checkOnlyCancellation.setValue(false);
                // this.checkOnlyInterruption.setValue(false);
                // this.checkOnlyRequest.setValue(false);
                // this.checkOnlyRevocation.setValue(false);
                // this.checkOnlySuspension.setValue(false);
            }
        },

        getToolbar: function(cf) {
            if (!this.toolbar) {

                this.findText = new Ext.form.TextField({
                    width: 280,
                    enableKeyEvents: true,
                    emptyText: 'Informe o texto a ser pesquisado e clique em Localizar.',
                    listeners: {
                        scope: this,
                        keypress: function(text, event) {
                            if (event.getCharCode() == event.RETURN || event.getCharCode() == event.TAB) {
                                this.setFilter();
                            }
                        }
                    }
                });

                var fields = this.getFindFields(cf);

                if (fields.length > 0)
                    this.fieldsToSearch = new Ext.Button({
                        text: 'Localizar:',
                        menu: fields
                    });
                else
                    this.fieldsToSearch = new Ext.form.Label({
                        text: 'Localizar:'
                    });

                this.dataInicioFind = new Ext.form.DateField({
                    emptyText: 'Início',
                    format: 'd/m/Y',
                    id: 'data_inicio',
                    width: 90,
                    enableKeyEvents: true,
                    listeners: {
                        scope: this,
                        keypress: function(text, event) {
                            if (event.getCharCode() == event.RETURN || event.getCharCode() == event.TAB) {
                                this.setFilter();
                            }
                        }
                    }
                });
                this.dataFimFind = new Ext.form.DateField({
                    emptyText: 'Fim',
                    format: 'd/m/Y',
                    id: 'data_fim',
                    width: 90,
                    enableKeyEvents: true,
                    listeners: {
                        scope: this,
                        keypress: function(text, event) {
                            if (event.getCharCode() == event.RETURN || event.getCharCode() == event.TAB) {
                                this.setFilter();
                            }
                        }
                    }
                });
                this.checkAlteracao = new Ext.form.Checkbox({
                    name: 'check_alteracao',
                    boxLabel: 'Alterações',
                    fieldLabel: 'Buscar alterações',
                    xtype: 'checkbox',
                    checked: false
                });

                this.toolbar = new Ext.Toolbar({
                    items: [
                        this.getToolbarClass(),
                        '-',
                        // ' ',
                        this.fieldsToSearch,
                        ' ',
                        this.findText,
                        '-',
                        ' ',
                        this.checkAlteracao,
                        ' ',
                        '-',
                        this.dataInicioFind,
                        ' ',
                        this.dataFimFind,
                        '->',
                        {
                            xtype: 'button',
                            text: 'Localizar',
                            iconCls: true,
                            icon: '/' + global.Context + '/static/images/find.png',
                            handler: this.setFilter,
                            scope: this
                        },
                        ' ',
                        {
                            xtype: 'button',
                            text: 'Limpar',
                            iconCls: true,
                            icon: '/' + global.Context + '/static/images/clean.png',
                            handler: function() {
                                this.markFilter('all');
                                this.findText.setValue('');
                                this.dataInicioFind.setValue('');
                                this.dataFimFind.setValue('');
                                this.checkAlteracao.setValue(false);
                                this.setFilter();
                                this.findText.getEl().dom.focus();
                            },
                            scope: this
                        }
                    ]
                });
            }

            return this.toolbar;
        },

        getAfastamentoToolbarClass: function(){
            this.checkOnlyComparecimentoJuizo = new Ext.form.Checkbox({
                name: 'onlyComparecimentoJuizo',
                boxLabel: 'Comparecer em juízo',
                checked: true,
                scope: this
            });
            this.checkOnlyCandidatura = new Ext.form.Checkbox({
                name: 'onlyCandidatura',
                boxLabel: 'Candidatura',
                checked: true,
                scope: this
            });
            this.checkOnlyCompeticao = new Ext.form.Checkbox({
                name: 'onlyCompeticao',
                boxLabel: 'Competição desportiva ou representação cultural',
                checked: true,
                scope: this
            });
            this.checkOnlyCursoFormacaoConcurso = new Ext.form.Checkbox({
                name: 'onlyCursoFormacaoConcurso',
                boxLabel: 'Curso de formação de etapa de concurso público',
                checked: true,
                scope: this
            });
            this.checkOnlyDeslocamento = new Ext.form.Checkbox({
                name: 'onlyDeslocamento',
                boxLabel: 'Deslocamento até a nova sede',
                checked: true,
                scope: this
            });
            this.checkOnlyJusticaEleitoral = new Ext.form.Checkbox({
                name: 'onlyJusticaEleitoral',
                boxLabel: 'Convocação da Justiça Eleitoral',
                checked: true,
                scope: this
            });
            this.checkOnlyEstudar = new Ext.form.Checkbox({
                name: 'onlyEstudar',
                boxLabel: 'Estudar no País/Exterior',
                checked: true,
                scope: this
            });
            this.checkOnlyExercicioMandato = new Ext.form.Checkbox({
                name: 'onlyExercicioMandato',
                boxLabel: 'Exercício de Mandato Eletivo',
                controller: 'AFAAfastamentoMandatoEletivo',
                checked: true,
                scope: this
            });
            this.checkOnlyMissao = new Ext.form.Checkbox({
                name: 'onlyMissao',
                boxLabel: 'Missão Oficial no Exterior',
                controller: 'AFAAfastamentoMissao',
                checked: true,
                scope: this
            });
            this.checkOnlyPrisao = new Ext.form.Checkbox({
                name: 'onlyPrisao',
                boxLabel: 'Prisão',
                controller: 'AFAAfastamentoPrisao',
                checked: true,
                scope: this
            });
            this.checkOnlyServirOutroOrgao = new Ext.form.Checkbox({
                name: 'onlyServirOutroOrgao',
                boxLabel: 'Servir a outro Órgão',
                controller: 'AFAAfastamentoOutroOrgao',
                checked: true,
                scope: this
            });
            this.checkOnlyServirJuri = new Ext.form.Checkbox({
                name: 'onlyServirJuri',
                boxLabel: 'Servir no Tribunal do Juri',
                controller: 'AFAAfastamentoServirJuri',
                checked: true,
                scope: this
            });
            this.checkOnlySuspensao = new Ext.form.Checkbox({
                name: 'onlySuspensao',
                boxLabel: 'Suspensão',
                controller: 'AFAAfastamentoSuspensao',
                checked: true,
                scope: this
            });
            this.checkOnlyTreinamento = new Ext.form.Checkbox({
                name: 'onlyTreinamento',
                boxLabel: 'Treinamento (Palestras/Congressos/Seminários/Outros)',
                controller: 'AFAAfastamentoTreinamento',
                checked: true,
                scope: this
            });
            this.checkOnlySindicanciaAdm = new Ext.form.Checkbox({
                name: 'onlySindicanciaAdm',
                boxLabel: 'Suspensão',
                controller: 'AFAAfastamentoSindicanciaAdm',
                checked: true,
                scope: this
            });            
            this.checkOnlyRecessoForense = new Ext.form.Checkbox({
                name: 'onlyRecessoForense',
                boxLabel: 'Recesso Forense - Membros',
                controller: 'AFAAfastamentoRecessoForenseRestful',
                checked: true,
                scope: this
            });
        },

        getLicencaToolbarClass: function(){
            this.checkOnlyAfastamentoConjuge = new Ext.form.Checkbox({
                name: 'onlyAfastamentoConjuge',
                boxLabel: 'Afastamento do Cônjuge/Companheiro',
                checked: true,
                scope: this
            });
            this.checkOnlyAtividadePolitica = new Ext.form.Checkbox({
                name: 'onlyAtividadePolitica',
                boxLabel: 'Atividade Política',
                checked: true,
                scope: this
            });
            this.checkOnlyCapacitacao = new Ext.form.Checkbox({
                name: 'onlyCapacitacao',
                boxLabel: 'Capacitação ou Especialização (3 meses por quinquênio)',
                checked: true,
                scope: this
            });
            this.checkOnlyMandatoClassista = new Ext.form.Checkbox({
                name: 'onlyMandatoClassista',
                boxLabel: 'Desempenho de Mandato Classista',
                checked: true,
                scope: this
            });
            this.checkOnlyDoencaFamilia = new Ext.form.Checkbox({
                name: 'onlyDoencaFamilia',
                boxLabel: 'Doença em Pessoa da Família',
                checked: true,
                scope: this
            });
            this.checkOnlyMaternidade = new Ext.form.Checkbox({
                name: 'onlyMaternidade',
                boxLabel: 'Maternidade/Tutoria ou Adoção',
                checked: true,
                scope: this
            });
            this.checkOnlyServicoMilitar = new Ext.form.Checkbox({
                name: 'onlyServicoMilitar',
                boxLabel: 'Serviço militar',
                checked: true,
                scope: this
            });
            this.checkOnlyTratamento3dias = new Ext.form.Checkbox({
                name: 'onlyTratamento3dias',
                boxLabel: 'Tratamento de Saúde até 15 dias - Servidor',
                checked: true,
                scope: this
            });
            this.checkOnlyTratamento30dias = new Ext.form.Checkbox({
                name: 'onlyTratamento30dias',
                boxLabel: 'Tratamento de Saúde até 30 dias - Membro',
                checked: true,
                scope: this
            });
            this.checkOnlyTratamentoJuntaMedica = new Ext.form.Checkbox({
                name: 'onlyTratamentoJuntaMedica',
                boxLabel: 'Tratamento de Saúde Junta Médica',
                checked: true,
                scope: this
            });
            this.checkOnlyInteresseParticular = new Ext.form.Checkbox({
                name: 'onlyInteresseParticular',
                boxLabel: 'Interesse Particular',
                checked: true,
                scope: this
            });
            this.checkOnlyTutoria = new Ext.form.Checkbox({
                name: 'onlyTutoria',
                boxLabel: 'Tutoria ou Adoção',
                checked: true,
                scope: this
            });
        },

        getAusenciaToolbarClass: function(){
            this.checkOnlyAlistamentoEleitor = new Ext.form.Checkbox({
                name: 'onlyAlistamentoEleitor',
                boxLabel: 'Alistamento como eleitor',
                checked: true,
                scope: this
            });
            this.checkOnlyCasamento = new Ext.form.Checkbox({
                name: 'onlyCasamento',
                boxLabel: 'Casamento',
                checked: true,
                scope: this
            });
            this.checkOnlyDoacaoSangue = new Ext.form.Checkbox({
                name: 'onlyDoacaoSangue',
                boxLabel: 'Doação de sangue',
                checked: true,
                scope: this
            });
            this.checkOnlyFalecimento = new Ext.form.Checkbox({
                name: 'onlyFalecimento',
                boxLabel: 'Falecimento (Luto)',
                checked: true,
                scope: this
            });
            this.checkOnlyConclusaoTcc = new Ext.form.Checkbox({
                name: 'onlyConclusaoTcc',
                boxLabel: 'Conclusão de TCC',
                checked: true,
                scope: this
            });
            this.checkOnlyNascimento = new Ext.form.Checkbox({
                name: 'onlyNascimento',
                boxLabel: 'Paternidade/Tutoria ou Adoção',
                checked: true,
                scope: this
            });
        },

        getToolbarClass: function(){
            this.getAfastamentoToolbarClass();
            this.getLicencaToolbarClass();
            this.getAusenciaToolbarClass();

            this.checkOnlyAtivo = new Ext.form.Checkbox({
                name: 'onlyAtivo',
                boxLabel: 'ATIVO',
                checked: true,
                scope: this
            });
            this.checkOnlyAgendado = new Ext.form.Checkbox({
                name: 'onlyAgendado',
                boxLabel: 'AGENDADO',
                checked: true,
                scope: this
            });
            this.checkOnlyCancelado = new Ext.form.Checkbox({
                name: 'onlyCancelado',
                boxLabel: 'CANCELADO',
                checked: this.departamento == 'expediente' ? true : false,
                scope: this
            });
            this.checkOnlyEncerrado = new Ext.form.Checkbox({
                name: 'onlyEncerrado',
                boxLabel: 'ENCERRADO',
                checked: this.departamento == 'expediente' ? true : false,
                scope: this
            });
            this.checkOnlyAtuacaoGrupoTrabalho = new Ext.form.Checkbox({
                name: 'onlyAtuacaoGrupoTrabalho',
                boxLabel: 'Atuação Grupo de Trabalho',
                checked: true,
                scope: this
            });
            this.checkOnlyAfastamento = new Ext.form.Checkbox({
                name: 'onlyAfastamento',
                boxLabel: 'Afastamento',
                checked: true,
                scope: this
            });
            this.checkOnlyAusencia = new Ext.form.Checkbox({
                name: 'onlyAusencia',
                boxLabel: 'Ausência',
                checked: true,
                scope: this
            });
            this.checkOnlyDesempenhoFuncao = new Ext.form.Checkbox({
                name: 'onlyDesempenhoFuncao',
                boxLabel: 'Desempenho de Função',
                checked: true,
                scope: this
            });
            this.checkOnlyFerias = new Ext.form.Checkbox({
                name: 'onlyFerias',
                boxLabel: 'Férias',
                checked: true,
                scope: this
            });
            this.checkOnlyFolgaCompensacao = new Ext.form.Checkbox({
                name: 'onlyFolgaCompensacao',
                boxLabel: 'Folga Compensação',
                checked: true,
                scope: this
            });
            this.checkOnlyFolgaEleitoral = new Ext.form.Checkbox({
                name: 'onlyFolgaEleitoral',
                boxLabel: 'Folga Eleitoral',
                checked: true,
                scope: this
            });
            this.checkOnlyFolgaAniversario = new Ext.form.Checkbox({
                name: 'onlyFolgaAniversario',
                boxLabel: 'Folga Aniversário',
                checked: true,
                scope: this
            });
            this.checkOnlyLicenca = new Ext.form.Checkbox({
                name: 'onlyLicenca',
                boxLabel: 'Licença',
                checked: true,
                scope: this
            });
            this.checkOnlyPlantao = new Ext.form.Checkbox({
                name: 'onlyPlantao',
                boxLabel: 'Plantão de Feriado',
                checked: true,
                scope: this
            });
            this.checkOnlyViagem = new Ext.form.Checkbox({
                name: 'onlyViagem',
                boxLabel: 'Viagem',
                checked: true,
                scope: this
            });
            this.checkOnlyRecesso = new Ext.form.Checkbox({
                name: 'onlyRecesso',
                boxLabel: 'Recesso',
                checked: true,
                scope: this
            });
            // this.checkOnlyCancellation = new Ext.form.Checkbox({
            //     name: 'onlyCancellation',
            //     boxLabel: 'Cancelado',
            //     checked: true,
            //     scope: this
            // });
            this.checkOnlyInterruption = new Ext.form.Checkbox({
                name: 'onlyInterruption',
                boxLabel: 'Interrupção',
                checked: true,
                scope: this
            });
            this.checkOnlyRequest = new Ext.form.Checkbox({
                name: 'onlyRequest',
                boxLabel: 'Alteração a pedido',
                checked: true,
                scope: this
            });
            this.checkOnlyRevocation = new Ext.form.Checkbox({
                name: 'onlyRevocation',
                boxLabel: 'Revogação',
                checked: true,
                scope: this
            });
            this.checkOnlySuspension = new Ext.form.Checkbox({
                name: 'onlySuspension',
                boxLabel: 'Suspensão',
                checked: true,
                scope: this
            });

            return [
                {
                    text:'Afastamentos',
                    iconCls: true,
                    icon: "/" + global.Context + "/static/engine/images/icons/athenas-0460.png",
                    menu: this.getMenuNovo()
                },
                '-',
                // {
                //     text: 'Anotação',
                //     iconCls: true,
                //     icon: "/" + global.Context + "/static/engine/images/icons/athenas-0333.png",
                //     handler: function() {
                //         if(this.getSelectionModel().getSelected().get("anotacao")){
                //             new toolkit.rh.utils.ExtCrudCall({
                //                 controller: this.getSelectionModel().getSelected().get("anotacao_class"),
                //                 pk: this.getSelectionModel().getSelected().get("anotacao"),
                //                 tipo: 'EDIT',
                //                 fields: [],
                //                 store: this.getStore()
                //             }).call();
                //         }else{ alert('Este afastamento não possui anotação!');}
                //     },
                //     scope: this
                // },
                // '-',
                {
                    text: 'Substituições',
                    iconCls: true,
                    icon: "/" + global.Context + "/static/engine/images/icons/athenas-0246.png",
                    handler: this.callSubstituicoesInativacoes,
                    scope: this
                },
                '-',
                {
                    text: 'Filtro',
                    icon: '/' + global.Context + '/static/rh/images/conf-filtro.png',
                    scope: this,
                    menu: [
                        {
                            text: 'Selecionar',
                            scope: this,
                            menu: [
                                {
                                    text: ' Todos',
                                    xtype: 'button',
                                    scope: this,
                                    handler: function(){ this.markFilter('all')},
                                },
                                {
                                    text: ' Nenhum',
                                    xtype: 'button',
                                    scope: this,
                                    handler: function(){ this.markFilter('none')},
                                }
                            ]
                        },
                        {
                            text: 'Tipos de Servidores',
                            scope: this,
                            menu: [
                                {
                                    text: 'Todos',
                                    group: 'tipoServidor',
                                    value: '',
                                    checked: this.departamento == 'expediente' ? false : true,
                                    scope: this,
                                    handler: this.toggleOnlyTipoServidor
                                },{
                                    text: 'Estagiários',
                                    group: 'tipoServidor',
                                    value: 'E',
                                    checked: false,
                                    scope: this,
                                    handler: this.toggleOnlyTipoServidor
                                },{
                                    text: 'Administrativos',
                                    group: 'tipoServidor',
                                    value: 'S',
                                    checked: false,
                                    scope: this,
                                    handler: this.toggleOnlyTipoServidor
                                },{
                                    text: 'Membros',
                                    group: 'tipoServidor',
                                    value: 'M',
                                    checked: this.departamento == 'expediente' ? true : false,
                                    scope: this,
                                    handler: this.toggleOnlyTipoServidor
                                }
                            ]
                        },
                        {
                            text: 'Situação',
                            scope: this,
                            menu: [
                                this.checkOnlyAtivo,
                                this.checkOnlyAgendado,
                                this.checkOnlyCancelado,
                                this.checkOnlyEncerrado
                            ]
                        },
                        {
                            text: 'Tipo de alteração',
                            scope: this,
                            menu: [
                                // this.checkOnlyCancellation,
                                this.checkOnlyInterruption,
                                this.checkOnlyRequest,
                                this.checkOnlyRevocation,
                                this.checkOnlySuspension,
                            ]
                        },
                        {
                            text: 'Afastamentos -> ',
                            scope: this,
                            menu: [
                                this.checkOnlyComparecimentoJuizo,
                                this.checkOnlyCandidatura,                                
                                this.checkOnlyCompeticao,
                                this.checkOnlyCursoFormacaoConcurso,
                                this.checkOnlyDeslocamento,
                                this.checkOnlyJusticaEleitoral,
                                this.checkOnlyEstudar,
                                this.checkOnlyExercicioMandato,
                                this.checkOnlyMissao,
                                this.checkOnlyPrisao,
                                this.checkOnlyServirOutroOrgao,
                                this.checkOnlyServirJuri,
                                this.checkOnlySuspensao,
                                this.checkOnlyTreinamento,
                            ]
                        },
                        {
                            text: 'Licenças -> ',
                            scope: this,
                            menu: [
                                this.checkOnlyAfastamentoConjuge,
                                this.checkOnlyAtividadePolitica,
                                this.checkOnlyCapacitacao,
                                this.checkOnlyMandatoClassista,
                                this.checkOnlyDoencaFamilia,
                                this.checkOnlyMaternidade,
                                this.checkOnlyServicoMilitar,
                                this.checkOnlyTratamento3dias,
                                this.checkOnlyTratamento30dias,
                                this.checkOnlyTratamentoJuntaMedica,
                                this.checkOnlyInteresseParticular,
                                this.checkOnlyTutoria,
                            ]
                        },
                        {
                            text: 'Ausências -> ',
                            scope: this,
                            menu: [
                                this.checkOnlyAlistamentoEleitor,
                                this.checkOnlyCasamento,
                                this.checkOnlyDoacaoSangue,
                                this.checkOnlyFalecimento,
                                this.checkOnlyConclusaoTcc,
                                this.checkOnlyNascimento,
                            ]
                        },
                        // this.checkOnlyAfastamento,
                        this.checkOnlyAtuacaoGrupoTrabalho,
                        // this.checkOnlyAusencia,
                        this.checkOnlyDesempenhoFuncao,
                        this.checkOnlyFerias,
                        this.checkOnlyFolgaAniversario,
                        this.checkOnlyFolgaCompensacao,
                        this.checkOnlyFolgaEleitoral,
                        // this.checkOnlyLicenca,
                        this.checkOnlyPlantao,
                        this.checkOnlyViagem,
                        this.checkOnlyRecesso
                    ]
                }
            ];
        },

        getSecondToolBar: function(){
            if (!this.secondToolBar) {
                this.dataInicioFind = new Ext.form.DateField({
                    emptyText: 'Início',
                    format: 'd/m/Y',
                    id: 'data_inicio',
                    width: 90,
                    enableKeyEvents: true,
                    listeners: {
                        scope: this,
                        keypress: function(text, event) {
                            if (event.getCharCode() == event.RETURN || event.getCharCode() == event.TAB) {
                                this.setFilter();
                            }
                        }
                    }
                });
                this.dataFimFind = new Ext.form.DateField({
                    emptyText: 'Fim',
                    format: 'd/m/Y',
                    id: 'data_fim',
                    width: 90,
                    enableKeyEvents: true,
                    listeners: {
                        scope: this,
                        keypress: function(text, event) {
                            if (event.getCharCode() == event.RETURN || event.getCharCode() == event.TAB) {
                                this.setFilter();
                            }
                        }
                    }
                });
                this.checkAlteracao = new Ext.form.Checkbox({
                    name: 'check_alteracao',
                    boxLabel: 'Alterações',
                    fieldLabel: 'Buscar alterações',
                    xtype: 'checkbox',
                    checked: false
                });
                this.secondToolBar = new Ext.Toolbar({
                    items: [
                        ' ',
                        this.checkAlteracao,
                        '-',
                        this.dataInicioFind,
                        ' ',
                        this.dataFimFind,
                        '->',
                        {
                            xtype: 'button',
                            text: 'Localizar',
                            iconCls: true,
                            icon: '/' + global.Context + '/static/images/find.png',
                            handler: this.setFilter,
                            scope: this
                        },
                        ' ',
                        {
                            xtype: 'button',
                            text: 'Limpar',
                            iconCls: true,
                            icon: '/' + global.Context + '/static/images/clean.png',
                            handler: function() {
                                this.markFilter('all');
                                this.findText.setValue('');
                                this.dataInicioFind.setValue('');
                                this.dataFimFind.setValue('');
                                this.checkAlteracao.setValue(false);
                                this.setFilter();
                                this.findText.getEl().dom.focus();
                            },
                            scope: this
                        }
                    ]
                });
            }
            return this.secondToolBar;
        },

        toggleOnlyTipoServidor: function(menuItem) {
            if(menuItem.value == '')
                delete(this.getStore().baseParams.tipoServidor);
            else
                this.getStore().baseParams['tipoServidor'] = menuItem.value;
            this.getStore().load({});
        },

        chamarExtCrud: function(params){
            params.store = (params.store == undefined ? this.getStore() : params.store);
            new toolkit.rh.gestorafastamento.utils.ExtCrudCall(params).call();
        },

        callSubstituicoesInativacoes: function(){
            if(this.getSelectionModel().getSelected()){
                if(this.getSelectionModel().getSelected().get("status") == 'CANCELADO')
                    alert("Afastamento CANCELADO!");
                else{
                    new toolkit.rh.gestorafastamento.WindowSubstituicaoInativacao({
                        "store_afastamento": this.getStore(),
                        "servidor_tipo": this.getSelectionModel().getSelected().get("servidor_tipo"),
                        "label_servidor": this.getSelectionModel().getSelected().get("servidor") +
                            ' | AFASTADO DE ' + this.getSelectionModel().getSelected().get("data_inicio") +
                            ' A ' + (this.getSelectionModel().getSelected().get("data_fim") != '' ? this.getSelectionModel().getSelected().get("data_fim") : '--------'),
                        "afastamento": this.getSelectionModel().getSelected().get("pk"),
                        "servidor": this.getSelectionModel().getSelected().get("servidor_matricula"),
                        "servidor_pk": this.getSelectionModel().getSelected().get("servidor_pk")
                    }).show();
                }
            }else{
                Ext.MessageBox.show({
                   title: 'Informação',
                   msg: 'Selecione o servidor!',
                   buttons: Ext.MessageBox.OK,
                   icon: Ext.MessageBox.INFO
                });
                return;
            }
        }
    }),

    WindowSubstituicaoInativacao: Ext.extend(Ext.Window,{
        constructor: function(args) {
            var cf = {
                title: "SUBSTITUIÇÕES DE " + args.label_servidor,
                closable: true,
                resizable: false,
                modal: true,
                border: false,
                width: 720,
                height: 540,
                items: [
                    new toolkit.rh.gestorafastamento.GestorTabPanelSubstituicaoInativacao(args)
                ]
            };
            toolkit.rh.gestorafastamento.WindowSubstituicaoInativacao.superclass.constructor.call(this, cf);
        }
    }),

    GestorTabPanelSubstituicaoInativacao: Ext.extend(Ext.TabPanel,{
        constructor: function(args) {
            var cf = {
                activeTab: 0,
                tabPosition: 'top',
                border: false,
                autoRender: true,
                items:[
                    new toolkit.rh.gestorafastamento.SubstituicaoInativacaoPanel({args: args}),
                    new toolkit.rh.gestorafastamento.SubstituicaoAgendadaGridPanel({servidor: args.servidor})
                ]
            };
            toolkit.rh.gestorafastamento.GestorTabPanelSubstituicaoInativacao.superclass.constructor.call(this, cf);
        }
    }),

    SubstituicaoInativacaoPanel: Ext.extend(Ext.Panel,{
        constructor: function(cf) {
            cf.title = 'Substituições e Inativações';
            cf.items = [];
            var buttons = [];
            var substituicaoGridPanel = undefined;
            if(cf.args.servidor_tipo == "servidor"){
                cf.args.controller = "RHMovimentacaoSubstituicao";
                cf.args.height = 480;
                var grid_name = 'rh.movimentacao.substituicao.DepartureGrid';
            }else
                var grid_name = 'rh.movimentacao.substituicaomembro.DepartureGrid';

            substituicaoGridPanel = Ext._create(
                grid_name,
                {
                    departure: cf.args.afastamento,
                    employee: cf.args.servidor_pk,
                    employee_registry: cf.args.servidor,
                    gridAutoLoad: false
                }
            );

            substituicaoGridPanel.setFilterProperty('afastamento__pk', cf.args.afastamento);
            substituicaoGridPanel.setSortProperty('data_inicio', 'DESC');

            cf.items.push(substituicaoGridPanel);

            if(cf.args.servidor_tipo == "membro"){
                var memberGrid = Ext._create(
                    'rh.inativacaocargomembro.DepartureGrid',
                    {
                        departure: cf.args.afastamento,
                        employee: cf.args.servidor_pk,
                        employee_registry: cf.args.servidor,
                    }
                );
                memberGrid.setFilterProperty('afastamento__servidor__matricula', cf.args.servidor)
                cf.items.push(memberGrid);
                cf.items.push(new Ext.Panel({
                    border: false,
                    frame: true,
                    height: 40,
                    buttonAlign: "right",
                    buttons: buttons
                }));
            }

            cf.listeners = {
                scope: this,
                beforeshow: function(component){
                    component.getComponent(0).getStore().load();
                    if(cf.args.servidor_tipo == "membro")
                        component.getComponent(1).getStore().load();
                }
            };
            toolkit.rh.gestorafastamento.SubstituicaoInativacaoPanel.superclass.constructor.call(this, cf);
        }
    }),

    InativacaoGridPanel: Ext.extend(toolkit.rh.utils.CustomGridPanel,{
        constructor: function(args) {
            this.afastamento = args.afastamento;
            this.servidor = args.servidor;
            var cf = {
                title: 'Inativações',
                height: 210,
                searchable: true,
                border: false,
                controller: 'RHInativacaoCargoMembro',
                pageSize: 3,
                readerFields: [
                    {name: 'pk'},
                    {name: 'posse'},
                    {name: 'data_inicio'},
                    {name: 'data_fim'},
                    {name: 'data_prevista'},
                    {name: 'situacao'}
                ],
                listeners: {
                    scope: this,
                    dblclick: function() { this.callWindowFormInativacaoMembro('EDIT'); },
                    beforeshow: function(component){ this.getStore().load(); }
                }
            };
            toolkit.rh.gestorafastamento.InativacaoGridPanel.superclass.constructor.call(this, cf);
        },

        callWindowFormInativacaoMembro: function(tipo){
            var inativacao = undefined;
            if(tipo == 'EDIT'){
                if(this.getSelectionModel().getSelected()){
                    inativacao = this.getSelectionModel().getSelected().get("pk");
                }else{
                    Ext.MessageBox.show({
                       title: 'Informação',
                       msg: 'Selecione uma inativação!',
                       buttons: Ext.MessageBox.OK,
                       icon: Ext.MessageBox.INFO
                    });
                    return;
                }
            }
            new toolkit.rh.gestorafastamento.WindowFormInativacaoMembro({
                "inativacao": inativacao,
                "afastamento": this.afastamento,
                "servidor": this.servidor,
                "store_call_back": this.getStore()
            }).show();
        },

        getStore: function(){
            var store = toolkit.rh.gestorafastamento.InativacaoGridPanel.superclass.getStore.call(this, {});
            store.baseParams.servidor = this.servidor;
            store.baseParams.afastamento = this.afastamento;
            store.baseParams.geral = false;
            return store;
        },

        getColumnModel: function(){
            if(!this.colModelGridPanel){
                this.colModelGridPanel = new Ext.grid.ColumnModel({
                    columns: [
                        {header: "Código", sortable: false, dataIndex: "pk", key: "pk", id: "pk", width: 50},
                        {header: "Cargo", sortable: false, dataIndex: "posse", key: "posse", id: "posse", width: 310},
                        {header: "Situação", sortable: true, dataIndex: "situacao", key: "situacao", width: 70},
                        {header: "Início", sortable: true, dataIndex: "data_inicio", key: "data_inicio", width: 85},
                        {header: "Prevista", sortable: true, dataIndex: "data_prevista", key: "data_prevista", width: 85},
                        {header: "Fim", sortable: true, dataIndex: "data_fim", key: "data_fim", width: 85}
                    ]
                });
            }
            return this.colModelGridPanel;
        },

        getToolbar: function(){
            var tbar = toolkit.rh.gestorafastamento.InativacaoGridPanel.superclass.getToolbar.call(this, {});
            tbar.insertButton(1, {
                    iconCls: true,
                    icon: "/" + global.Context + "/static/images/add.png",
                    handler: function() { this.callWindowFormInativacaoMembro(); },
                    scope: this
                });
            tbar.insertButton(2, '-');
            tbar.insertButton(3, {
                    iconCls: true,
                    icon: "/" + global.Context + "/static/images/edit.png",
                    handler: function() { this.callWindowFormInativacaoMembro('EDIT'); },
                    scope: this
                });
            tbar.insertButton(4, '-');
            tbar.insertButton(5, {
                    iconCls: true,
                    icon: "/" + global.Context + "/static/images/delete.png",
                    handler: function() {
                        if(this.getSelectionModel().getSelected()){
                            var id = this.getSelectionModel().getSelected().get("pk");
                            var fn = function(bnt, text, opts) {
                                if(bnt == "yes") {
                                    var obj = toolkit.util.Ajax.request_json(
                                        "POST",
                                        toolkit.util.Normalize.controller_action(
                                            this.controller,
                                            "commit",
                                            ["DELETE", id, 0])
                                    );
                                    var store = this.getStore();
                                    setTimeout(function() { store.load(); }, 100);
                                }
                                else if(bnt == "no") {
                                    this.callWindowFormInativacaoMembro('EDIT');
                                }
                                else {
                                    Ext.MessageBox.show({
                                        title: "Sistema Administrativo",
                                        msg : "A ação de remoção foi cancelada.",
                                        buttons: Ext.MessageBox.OK,
                                        icon: Ext.MessageBox.INFO
                                    });
                                }

                            }
                            Ext.MessageBox.show({
                                title: "ManagerNetWork",
                                msg : "Tem certeza que deseja remover o item com id " + id + ", \n\
                                    caso não tenha certeza clique em <b>Não</b> para visualizar os dados. \n\
                                    <b>TODAS substituições</b> agendadas para este afastamento serão apagadas!",
                                fn : fn,
                                scope: this,
                                buttons: Ext.MessageBox.YESNOCANCEL,
                                icon: Ext.MessageBox.QUESTION
                            });
                        }else{ alert('Escolha uma inativação!');}
                    },
                    scope: this
                });
            tbar.insertButton(6, '-');
            return tbar;
        }
    }),

    SubstituicaoAgendadaGridPanel: Ext.extend(toolkit.rh.utils.CustomGridPanel,{
        constructor: function(args) {
            this.servidor = args.servidor;
            var cf = {
                title: 'Agendamentos',
                height: 445,
                searchable: true,
                region: 'center',
                border: false,
                controller: 'RHMovimentacaoSubstituicaoMembro',
                pageSize: 10,
                readerFields: [
                    {name: 'pk'},
                    {name: 'data_inicio'},
                    {name: 'data_fim'},
                    {name: 'data_prevista'},
                    {name: 'substituido'},
                    {name: 'cargo'},
                    {name: 'situacao'}
                ],
                listeners:{
                    scope: this,
                    beforeshow: function(component){ this.getStore().load(); }
                }
            };
            toolkit.rh.gestorafastamento.SubstituicaoAgendadaGridPanel.superclass.constructor.call(this, cf);
        },

        getProxy: function(){
            if(!this.proxyGridPanel){
                this.proxyGridPanel = new Ext.data.HttpProxy({
                    scope: this,
                    method: 'POST',
                    api: {
                        read : toolkit.util.Normalize.controller_action(this.cf.controller, 'list_agendada'),
                        create : toolkit.util.Normalize.controller_action(this.cf.controller, 'create'),
                        update: toolkit.util.Normalize.controller_action(this.cf.controller, 'update'),
                        destroy: toolkit.util.Normalize.controller_action(this.cf.controller, 'delete')
                    }
                });
            }
            return this.proxyGridPanel;
        },

        getColumnModel: function(){
            if(!this.colModelGridPanel){
                this.colModelGridPanel = new Ext.grid.ColumnModel({
                    columns: [
                        {header: "Código", sortable: false, dataIndex: "pk", key: "pk", id: "pk", width: 50},
                        {header: "Cargo", sortable: false, dataIndex: "cargo", key: "cargo", id: "cargo", width: 183},
                        {header: "Substituido", sortable: false, dataIndex: "substituido", key: "substituido", id: "substituido", width: 184},
                        {header: "Situação", sortable: true, dataIndex: "situacao", key: "situacao", width: 60},
                        {header: "Início", sortable: true, dataIndex: "data_inicio", key: "data_inicio", width: 70},
                        {header: "Prevista", sortable: true, dataIndex: "data_prevista", key: "data_prevista", width: 70},
                        {header: "Fim", sortable: true, dataIndex: "data_fim", key: "data_fim", width: 70}
                    ]
                });
            }
            return this.colModelGridPanel;
        },

        getStore: function(){
            var store = toolkit.rh.gestorafastamento.SubstituicaoAgendadaGridPanel.superclass.getStore.call(this, {});
            store.baseParams.servidor = this.servidor;
            store.baseParams.agendada = true;
            return store;
        }
    }),

    WindowFormInativacaoMembro: Ext.extend( Ext.Window,{
        constructor: function(args) {
            this.inativacao = args.inativacao ? args.inativacao : undefined;
            this.data_inativacao = this.getData(this.inativacao);
            this.afastamento = args.afastamento ? args.afastamento : undefined;
            this.servidor = args.servidor ? args.servidor : undefined;
            this.store_call_back = args.store_call_back ? args.store_call_back: undefined;
            var cf = {
                title: 'Inativação de Cargo de Membros',
                closable: true,
                resizable: false,
                modal: true,
                border: false,
                width: 530,
                autoHeight: true,
                items:[ this.getForm() ]
            };
            toolkit.rh.gestorafastamento.WindowFormInativacaoMembro.superclass.constructor.call(this, cf);
        },

        getForm: function(){
            if(this.form == undefined){
                this.form = new Ext.form.FormPanel({
                    border: false,
                    buttonAlign: "right",
                    buttons: [
                        {
                            text: "Salvar",
                            handler: function(){ this.commit(); },
                            scope: this
                        },
                        {
                            text: "Cancelar",
                            handler: function() { this.destroy(); },
                            scope: this
                        }
                    ],
                    items: [ this.getFields() ]
                });
            }
            return this.form;
        },

        getData: function(){
            if(this.inativacao != undefined){
                var obj = toolkit.util.Ajax.request_json(
                        "POST",
                        toolkit.util.Normalize.controller_action(
                            "RHInativacaoCargoMembro","get_data"
                        ),
                        { inativacao: this.inativacao }
                );
                return obj;
            }else return undefined;
        },

        commit: function() {
            var tipo = ((this.inativacao != undefined) ? (tipo = "/EDIT/" + this.inativacao) : "/NEW/0");
            var params = {"afastamento":this.afastamento};
            if(this.inativacao != undefined)
                params = {"afastamento": this.afastamento, "cargo_arquimedes": this.data_inativacao.cargo_arquimedes};
            var form = this.getForm().getForm();
            form.submit({
                scope: this,
                clientValidation: true,
                url: toolkit.util.Normalize.controller_action(
                    "RHInativacaoCargoMembro", "commit" + tipo
                ),
                params: params,
                success: function(form, action){
                    if(action.result.result){
                        this.store_call_back.load();
                        this.destroy();
                    }else{
                        alert(action.result.messageException);
                    }
                },
                failure: function(form, action){
                    if(action.result.result){
                        this.store_call_back.load();
                        this.destroy();
                    }else{
                        alert(action.result.messageException);
                    }
                },
                waitMsg: "salvando..."
            });
        },

        getStore: function(controller, params){
            return toolkit.util.Ajax.request_json(
                "POST", toolkit.util.Normalize.controller_action(controller, "get_store"), params);
        },

        getFields: function(){
            return toolkit.rh.gestorafastamento.utils.FormInativacaoMembroFields({father: this});
        }
    })
});
