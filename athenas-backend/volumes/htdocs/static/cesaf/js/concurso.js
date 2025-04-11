//TODO: Realizar alteração para listar as incrições por concurso, atualmente todas estão sendo listadas.

if(typeof(toolkit.cesaf.concurso) == 'undefined')
{
    Ext.ns('toolkit.cesaf.concurso');

   /*************** Gestor Recursos ****************/
   toolkit.cesaf.concurso.GestorRecurso = Ext.extend(
        Ext.Window,
        {
            constructor: function(inscricao)
            {
                this.inscricao = inscricao;
                var cf = {
                    title: 'Recursos',
                    closable: true,
                    modal:true,
                    layout:'border',
                    height: 500,
                    width: 600,
                    defaults:{margins:'0 0 5 0'}
                };

                toolkit.cesaf.concurso.GestorRecurso.superclass.constructor.call(this, cf);

                this.add(this.getPanelRecursos());
                this.add(this.getPanelRecursoView());
            },

            getFormDeferirIndeferir: function(act, recurso)
            {
                var form = new Ext.FormPanel({
                    labelAlign:'top',
                    labelWidth: 125,
                    border:false,
                    frame:true,
                    region:'center',
                    defaults: {width: 570, height:300},
                    items: [
                        {
                            name: 'tipo',
                            id: 'tipo',
                            value: act,
                            xtype: 'hidden'
                        },
                        {
                            name: 'inscricao',
                            id: 'inscricao',
                            value: this.inscricao,
                            xtype: 'hidden'
                        },
                        {

                            name: 'recurso',
                            id: 'recurso',
                            value: recurso,
                            xtype: 'hidden'
                        },
                        {
                            fieldLabel: 'Parecer',
                            name: 'parecer',
                            id: 'parecer',
                            xtype: 'xhtmleditor'
                        }
                    ]
                });

                form.addButton({
                    text:'OK',
                    scope:this,
                    handler:function(f)
                    {
                        form.getForm().submit({
                            url:toolkit.util.Normalize.controller_action('CONCURSOGerenciador', 'deferir_recurso'),
                            waitMsg:'Processando...',
                            submitEmptyText: true,
                            scope:this,
                            success: function(form, action)
                            {
                                this.getStoreGridRecurso().reload();
                                this.getWindowForm().close();
                                this.getPanelRecursoView().removeAll();
                                Ext.Msg.alert('Aviso', action.result.msg);
                            },
                            failure: function(form, action)
                            {
                                switch (action.failureType)
                                {
                                    case Ext.form.Action.CLIENT_INVALID:
                                        Ext.Msg.alert('Falha', 'Os dados do formulário não são válidos');
                                        break;
                                    case Ext.form.Action.CONNECT_FAILURE:
                                        Ext.Msg.alert('Falha', 'A requisição ajax falhou');
                                        break;
                                    case Ext.form.Action.SERVER_INVALID:
                                       Ext.Msg.alert('Falha', action.result.msg);
                               }
                            }
                        });
                    }
                });
                return form;
            },

            getWindowForm: function(button)
            {
                if(!this.windowForm)
                {
                    var recurso = this.getPanelRecursos().getSelectionModel().getSelected().get('codigo');
                    this.windowForm = new Ext.Window({
                        title: (button.getText() == 'Deferir') ? 'Deferimento' : 'Indeferimento',
                        closable: true,
                        modal:true,
                        layout:'fit',
                        height: 400,
                        width: 600,
                        defaults:{margins:'0 0 5 0'},
                        items:this.getFormDeferirIndeferir(button.getText(), recurso),
                        listeners:{
                            scope:this,
                            close:function()
                            {
                                this.windowForm.destroy()
                                this.windowForm = null;
                            }
                        }
                    });
                }
                return this.windowForm;
            },

            deferirIndeferir: function(b)
            {
                if( this.getPanelRecursos().getSelectionModel().getSelected() )
                    this.getWindowForm(b).show();
                else
                    Ext.Msg.alert('Aviso', 'É necessário selecionar um recurso.');
            },

            getPanelRecursoView: function()
            {
                if( !this.recursoDetalhes )
                {
                    this.recursoDetalhes = new Ext.Panel({
                        region:'south',
                        height:300,
                        border:false,
                        split:true,
                        tbar:[
                            {
                                text:'Deferir',
                                scope:this,
                                handler:this.deferirIndeferir
                            },
                            {
                                text:'Indeferir',
                                scope:this,
                                handler:this.deferirIndeferir
                            }
                        ],
                        listeners:{
                            scope:this,
                            render:function()
                            { this.getStoreGridRecurso().load({ params:{ inscricao: this.inscricao } }); }
                        }
                    });
                }
                return this.recursoDetalhes;
            },

            getPanelRecursos: function()
            {
                if(!this.panelRecursos)
                {
                    this.panelRecursos = new Ext.grid.GridPanel({
                        region:'center',
                        cm: this.getRecursoColumnModel(),
                        store: this.getStoreGridRecurso(), //store do grid???
                        border: true,
                        height:500,
                        sm: new Ext.grid.RowSelectionModel({
                            singleSelect:true,
                            listeners: {
                                scope: this,
                                rowselect: function(sm)
                                {
                                    this.getPanelRecursoView().removeAll();
                                    this.getPanelRecursoView().add(
                                        new Ext.Panel({
                                            html:sm.getSelected().get('resumo'),
                                            border:false,
                                            style:{margin:'5px', lineHeight:'16px', fontSize:'12px'}
                                        })
                                    );
                                    this.getPanelRecursoView().doLayout();
                                }
                            }
                        }),
                        bbar: this.getRecursoGridPaginator(),
                    });
                }
                return this.panelRecursos;
            },

            getRecursoColumnModel: function()
            {
                if(!this.recursoColumnModel)
                {
                    this.recursoColumnModel = new Ext.grid.ColumnModel([
                        {dataIndex: 'codigo', header: 'Código', sortable: true, width: 150},
                        {dataIndex: 'assunto', header: 'Assunto', sortable: true, width: 450},
                    ]);
                }
                return this.recursoColumnModel;
            },

            getStoreGridRecurso: function()
            {
                if(!this.storeGridRecurso)
                {
                    this.storeGridRecurso = new Ext.data.JsonStore({
                        fields: ['codigo', 'assunto', 'resumo'],
                        root: 'result',
                        totalProperty: 'totalRows',
                        url: toolkit.util.Normalize.controller_action(
                            'CONCURSOGerenciador',
                            'recurso_por_inscricao',
                            [this.inscricao]
                        ),
                        baseParams:{ start:0, limit:50 },
                        remoteSort: true
                    });
                }
                return this.storeGridRecurso;
            },

            getRecursoGridPaginator: function()
            {
                if(!this.recursoGridPaginator)
                {
                    this.recursoGridPaginator = new Ext.PagingToolbar({
                        autoWidth: true,
                        store: this.getStoreGridRecurso(),
                        displayInfo: true,
                        pageSize: 50,
                        prependButtons: true
                    })
                }
                return this.recursoGridPaginator;
            }
        }
    );
    /*************** Gestor Recursos ****************/

    toolkit.cesaf.concurso.Gerenciador = Ext.extend(
        Ext.Panel,
        {
            _not_implemented: function(){
                console.debug("not implemented");
            },

            constructor: function(args) {
                var cf = {
                    title: 'Concurso',
                    closable: true,
                    layout: {
                        type:'vbox',
                        padding:'5',
                        align:'stretch'
                    },
                    defaults:{margins:'0 0 5 0'}

                };
                toolkit.cesaf.concurso.Gerenciador.superclass.constructor.call(this, cf);
                var active = toolkit.Application.tabspace.getActiveTab();
                toolkit.Application.tabspace.remove(active);
                toolkit.Application.tabspace.add(this);
                this.add(this.getPanelConcurso());
                this.add(this.getPanelInscricao());
                var obj = this;
                setTimeout(function() {obj.doLayout();}, 50);
                this.on('render',function() {this.getStoreGridConcurso().load({
                        params:{start: 0,limit: 50}});},this);
            },

            /**
             *
             *    PANEL CONCURSO
             *
             **/
            getPanelConcurso: function(){
                if(!this.panelConcurso){
                    this.panelConcurso = new Ext.grid.GridPanel({
                        height: 150,
                        title: "<b>Concurso</b>",
                        cm: this.getConcursoColumnModel(),
                        store: this.getStoreGridConcurso(), //store do grid???
                        border: true,
                        flex: 1,
                        sm: new Ext.grid.RowSelectionModel({
                            singleSelect:false,
                            listeners: {
                                 scope: this,
                                 rowselect: function(sm) {
                                    //alert(sm.getSelected().get('id'));
                                    this.getStoreGridInscricao().baseParams['concurso'] = sm.getSelected().get('codigo');
                                    this.getStoreGridInscricao().load({params:{start:0, limit:50}});
                                 }
                             }
                        }),
                        bbar: this.getConcursoGridPaginator(),
                        tbar: this.getConcursoGridToolbar(),
                        listeners: {
                             scope: this,
                             dblclick: function() {
                                if(this.panelConcurso.getSelectionModel().getSelected()){
                                   /*do something*/
                                }
                             }
                         }
                    });
                }
                return this.panelConcurso;
            },

            getFatherConcurso: function(tipo) {
                var father = false;
                var dict = {'concurso': 'MTOElementoDespesa'}
                father = {
                    store: this.getStoreGridConcurso(),
                    controller: dict[tipo],
                    reload_grid: function(){this.store.reload();}
                };
                return father;
            },

            getStoreGridConcurso: function() {
                if(!this.storeGridConcurso) {
                    this.storeGridConcurso = new Ext.data.JsonStore({
                        fields: [
                            "codigo",
                            "nome",
                            "dt_inicio",
                            "promovido_por",
                            "inscritos",
                            "homologados",
                            "descricao",
                            "slug"
                        ],
                        root: "result",
                        totalProperty: "totalRows",
                        url: toolkit.util.Normalize.controller_action(
                            "CONCURSOGerenciador",
                            "get_store",
                            ["concurso"]
                        ),
                        remoteSort: true
                    });
                }
                return this.storeGridConcurso;
            },

            getConcursoColumnModel: function() {
                if(!this.concursoColumnModel) {
                    this.concursoColumnModel = new Ext.grid.ColumnModel([
                        {dataIndex: 'codigo', header: 'Código', sortable: true, width: 50},
                        {dataIndex: 'nome', header: 'Nome', sortable: true, width: 300},
                        {dataIndex: 'dt_inicio', header: 'Data Início', sortable: true, width: 80},
                        {dataIndex: 'promovido_por', header: 'Promovido por', sortable: true, width: 80},
                        {dataIndex: 'inscritos', header: 'Inscritos', sortable: true, width: 80},
                        {dataIndex: 'homologados', header: 'Homologados', sortable: true, width: 80},
                        {dataIndex: 'descricao', header: 'Descrição', sortable: true, width: 200}
//                        {dataIndex: 'slug', header: 'slug', sortable: true, width: 200},
                    ]);
                }
                return this.concursoColumnModel;
            },

            getConcursoGridPaginator: function() {
                if(!this.gridPaginator) {
                    this.gridPaginator = new Ext.PagingToolbar({
                        autoWidth: true,
                        store: this.getStoreGridConcurso(),
                        displayInfo: true,
                        pageSize: 50,
                        prependButtons: true
                    })
                }
                return this.gridPaginator;
            },

            addConcurso: function(type) {
                new toolkit.widget.ExtCrudForm(
                    this.getFatherConcurso(type),
                    toolkit.widget.ExtCrudForm.TYPE.NEW,
                    false,
                    []
                ).show();
            },

            editConcurso: function() {
                if(this.panelConcurso.getSelectionModel().getSelected()){
                    new toolkit.widget.ExtCrudForm(
                        this.getFatherConcurso('concurso'),
                        toolkit.widget.ExtCrudForm.TYPE.EDIT,
                        this.panelConcurso.getSelectionModel().getSelected().get('codigo')
                    ).show();
                }
                else alert('Primeiro selecione uma capacitação para edição.')
            },

            deleteConcurso: function(record) {
                var controller = this.getFatherConcurso('concurso').controller;

                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action(
                        controller,
                        "commit",
                        ["DELETE", record.get("codigo"), 0]
                    ),
                    method: 'POST',
                    success: function() {
                        this.getStoreGridConcurso().reload();
                    },
                    scope: this
                });
            },

            deleteConcursos: function() {
                if(this.panelConcurso.getSelectionModel().getSelections()){
                    var items = this.panelConcurso.getSelectionModel().getSelections();
                    Ext.Msg.show({
                        title:'Apagar itens selecionados?',
                        msg: 'Deseja apagar os itens selecionados?',
                        buttons: Ext.Msg.YESNO,
                        fn: function(b) {if(b == "yes") Ext.each(items, this.deleteConcurso, this);},
                        icon: Ext.MessageBox.QUESTION,
                        scope: this
                    });
                }
                else alert("É necessário selecionar o(s) item(ns)!");
            },

            getConcursoGridToolbar: function() {
                var menu = [];
                menu.push({
                    text: "Relatórios",
                    iconCls: true,
                    icon: "/" + global.Context + "/static/cesaf/images/pdf.png",
                    menu: [
                        {
                            text: 'Concurso detalhado',
                            scope: this,
                            handler: this.openResume
                        }
                    ]
                });
                return menu;
            },

            openResume: function() {
                var selection = this.getPanelConcurso().getSelectionModel();

                if(selection.getSelected()) {
                    var rb = new toolkit.widget.ExtReportBuild(
                        'CONCURSOReport'
                    ).runReport(
                        'PDF',
                        {
                            concurso: selection.getSelected().get('codigo')
                        }
                    );
                }
                else alert('Para visualizar o resumo do concurso é necessário primeiro selecionar o concurso.');
            },

            /*****
             *
             *    PANEL INSCRICAO
             *
             **/
            getPanelInscricao: function(){
                if(!this.panelInscricao){
                    this.panelInscricao = new Ext.grid.GridPanel({
                        title: "<b>Inscrições</b>",
                        store: this.getStoreGridInscricao(),
                        cm: this.getInscricaoColumnModel(),
                        border: true,
                        flex: 1,
                        sm: new Ext.grid.RowSelectionModel({singleSelect:false}),
                        bbar: this.getInscricaoGridPaginator(),
                        tbar: this.getInscricaoGridToolbar(),
                        listeners: {
                            scope: this,
                            dblclick: function(){
                                new toolkit.cesaf.concurso.GestorRecurso(
                                    this.panelInscricao.getSelectionModel().getSelected().get('protocolo')
                                ).show();
                            }
                        }
                    });
                }
                return this.panelInscricao;
            },

            getStoreGridInscricao: function() {
                if(!this.storeGridInscricao) {
                    this.storeGridInscricao = new Ext.data.JsonStore({
                        fields: [
                            "codigo",
                            "protocolo",
                            "vaga_area",
                            "vaga_local",
                            "vaga_quantidade",
                            "faculdade",
                            "matricula",
                            "ano_periodo",
                            "disponibilidade",
//                            "inscricao",
                            "pessoa_nome",
                            "pessoa_cpf",
                            "data_criacao",
                            "status"
                        ],
                        root: "result",
                        totalProperty: "totalRows",
                        url: toolkit.util.Normalize.controller_action(
                            "CONCURSOGerenciador",
                            "get_store",
                            ["inscricao"]
                        ),
                        baseParams:{
                            concurso: "",
                            start:0,
                            limit:50
                        },
                        remoteSort: true
                    });
                }
                return this.storeGridInscricao;
            },

            getInscricaoColumnModel: function() {
                if(!this.inscricaoColumnModel) {
                    this.inscricaoColumnModel = new Ext.grid.ColumnModel([
                        {
                            dataIndex: 'status',
                            width: 40,
                            sortable: false,
                            header: '',
                            id: 'status',
                            renderer: toolkit.util.formatStatus,
                            menuDisabled: true
                        },
                        {dataIndex: 'codigo', header: 'Código', sortable: true, width: 50},
                        {dataIndex: 'protocolo', header: 'Nro. Inscrição', sortable: true, width: 120},
                        {dataIndex: 'data_criacao', header: 'Data', sortable: true, width: 100},
                        {dataIndex: 'pessoa_nome', header: 'Nome', sortable: true, width: 200},
                        {dataIndex: 'pessoa_cpf', header: 'CPF', sortable: true, width: 100},
                        {dataIndex: 'vaga_area', header: 'Área', sortable: true, width: 100},
                        {dataIndex: 'vaga_local', header: 'Local', sortable: true, width: 100},
//                        {dataIndex: 'inscricao', header: 'Inscrição', sortable: true, width: 300},
//                        {dataIndex: 'vaga_quantidade', header: 'vaga_quantidade', sortable: true, width: 100},
                        {dataIndex: 'curso', header: 'Curso', sortable: true, width: 100},
                        {dataIndex: 'faculdade', header: 'Faculdade', sortable: true, width: 100},
                        {dataIndex: 'matricula', header: 'Matrícula', sortable: true, width: 100},
                        {dataIndex: 'ano_periodo', header: 'Período', sortable: true, width: 50},
                        {dataIndex: 'ano_conclusao', header: 'Conclusão', sortable: true, width: 70},
                        {dataIndex: 'disponibilidade', header: 'Disponibilidade', sortable: true, width: 100}
                    ]);
                }
                return this.inscricaoColumnModel;
            },

            getInscricaoGridPaginator: function() {
                if(!this.inscricaoGridPaginator) {
                    this.inscricaoGridPaginator = new Ext.PagingToolbar({
                        autoWidth: true,
                        store: this.getStoreGridInscricao(),
                        displayInfo: true,
                        pageSize: 50,
                        prependButtons: true
                    })
                }
                return this.inscricaoGridPaginator;
            },

            getFatherInscricao: function() {
                return {
                    store: this.getStoreGridInscricao(),
                    controller: "MTOElementoDespesaSubItem",
                    reload_grid: function(){
                        this.store.reload();
                    }
                };
            },

            addInscricao: function() {
                if(this.panelConcurso.getSelectionModel().getSelected()) {
                    new toolkit.widget.ExtCrudForm(
                        this.getFatherInscricao(),
                        toolkit.widget.ExtCrudForm.TYPE.NEW,
                        false,
                        [{
                            name: "concurso",
                            enabled: false,
                            value: this.panelConcurso.getSelectionModel().getSelected().get('codigo')
                        }]
                    ).show();
                }
                else alert("Escolha um Concurso!")
            },

            editInscricao: function() {
                var selected = this.panelConcurso.getSelectionModel().getSelected();
                var iSelected = this.getPanelInscricao().getSelectionModel().getSelected();

                if(selected && iSelected) {
                    new toolkit.widget.ExtCrudForm(
                        this.getFatherInscricao(),
                        toolkit.widget.ExtCrudForm.TYPE.EDIT,
                        this.panelInscricao.getSelectionModel().getSelected().get('codigo'),
                        [{
                            name: "concurso",
                            enabled: false,
                            value: this.panelConcurso.getSelectionModel().getSelected().get('codigo')
                        }]
                    ).show();
                }
//                else alert("Escolha um Elemento de Despesa!")
            },

            deleteInscricao: function() {
                var selection = this.panelInscricao.getSelectionModel();

                if(selection.getSelections()) {
                    Ext.Msg.show({
                        title: 'Excluir as inscrições',
                        msg: 'Tem certeza que deseja excluir as inscrições selecionadas?',
                        buttons: Ext.Msg.YESNO,
                        fn: function(bnt) {
                            var ic = [];

                            if(bnt == 'yes') {
                                Ext.each(
                                    selection.getSelections(),
                                    function(record) {ic.push(record.get('codigo'))}
                                );

                                Ext.Ajax.request({
                                    url: toolkit.util.Normalize.controller_action(
                                        'MTOElementoDespesaSubItem',
                                        'delete'
                                    ),
                                    params: {
                                        inscricao: ic
                                    },
                                    success: function(request) {
                                        var result = Ext.decode(request.responseText);
                                        this.getStoreGridInscricao().reload();
                                    },
                                    failure: function() {
                                        alert('Ocorreu um erro tentando excluir as inscrições selecionadas.');
                                    },
                                    scope: this
                                })
                            }
                        },
                        icon: Ext.Msg.QUESTION,
                        scope: this
                    })
                }
                else alert('Primeiro você deve selecionar as inscrições que deseja excluir.')
            },

            getInscricaoGridToolbar: function() {
                if(!this.inscricaoToolbar) {
                    this.inscricaoToolbar = new Ext.Toolbar({
                        items: [
                            {
                                text: "Homologar",
                                iconCls: true,
                                icon: "/" + global.Context + "/static/cesaf/images/homologar.png",
                                scope: this,
                                handler: this.homologarInscricoes
                            },
                            '-',
                            {
                                iconCls: true,
                                icon: "/" + global.Context + "/static/cesaf/images/filter_search.png",
                                text: "Com Recurso",
                                scope:this,
                                handler:function()
                                { this.getStoreGridInscricao().load({params:{com_recurso:'ok', start:0, limit:50}}); }
                            },
                            {
                                iconCls: true,
                                icon: "/" + global.Context + "/static/cesaf/images/filter_search.png",
                                text: "Todas",
                                scope:this,
                                handler:function()
                                { this.getStoreGridInscricao().load({params:{start:0, limit:50}}); }
                            }
                        ]
                    });
                }

                return this.inscricaoToolbar;
            },

            homologarInscricoes: function() {
                var selection = this.panelInscricao.getSelectionModel();

                if(selection.getSelections()) {
                    Ext.Msg.show({
                        title: 'Homologar inscrições',
                        msg: 'Tem certeza que deseja homologar as incrições selecionadas?',
                        buttons: Ext.Msg.YESNO,
                        fn: function(bnt) {
                            var ic = [];

                            if(bnt == 'yes') {
                                Ext.each(
                                    selection.getSelections(),
                                    function(record) {ic.push(record.get('codigo'))}
                                );

                                Ext.Ajax.request({
                                    url: toolkit.util.Normalize.controller_action(
                                        'CONCURSOGerenciador',
                                        'homologar'
                                    ),
                                    params: {
                                        inscricao: ic
                                    },
                                    success: function(request) {
                                        var result = Ext.decode(request.responseText);
                                        this.getStoreGridInscricao().reload();
                                    },
                                    failure: function() {
                                        alert('Ocorreu um erro tentando homologar as incrições selecionadas.\nTente novamente mais tarde.');
                                    },
                                    scope: this
                                })
                            }
                        },
                        icon: Ext.Msg.QUESTION,
                        scope: this
                    })
                }
                else alert('Primeiro você deve selecionar as incrições que deseja homologar.');
            }

        }
    );
}

