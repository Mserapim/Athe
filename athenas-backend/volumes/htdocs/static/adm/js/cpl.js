if(typeof(toolkit.adm.cpl) == 'undefined') {

    Ext.ns('toolkit.adm.cpl');

    toolkit.adm.cpl.Gerenciador = Ext.extend(
        Ext.Panel,
        {
            _not_implemented: function(){ console.debug('not implemented'); },

            constructor: function(args) {
                var cf = {
                    title: 'Processo e Licitação',
                    border: false,
                    closable: false,
                    layout: 'border'
                };

                toolkit.adm.cpl.Gerenciador.superclass.constructor.call(this, cf);
                var active = toolkit.Application.tabspace.getActiveTab();
                toolkit.Application.tabspace.remove(active);
                toolkit.Application.tabspace.add(this);
                this.add(this.getPanelLicitacao());
                var obj = this;
                setTimeout(function() {obj.doLayout();}, 50);
                this.on('render', function() {this.getStoreGridLicitacao().load({params:{start: 0, limit: 50}});},this);
            },

            /*****
             *
             *    PANEL LICITAÇÃO
             *
             **/
            getPanelLicitacao: function(){
                if(!this.panelLicitacao){
                    this.panelLicitacao = new Ext.grid.GridPanel({
                        region: 'center',
                        border: false,
                        cm: this.getLicitacaoColumnModel(),
                        store: this.getStoreGridLicitacao(),
                        sm: new Ext.grid.RowSelectionModel({singleSelect:false}),
                        bbar: this.getLicitacaoGridPaginator(),
                        tbar: this.getLicitacaoGridToolbar(),
                        listeners: {
                            scope: this,
                            dblclick: function() {if(this.panelLicitacao.getSelectionModel().getSelected()) this.editLicitacao();}
                            }
                    });
                }
                return this.panelLicitacao;
            },

            getFatherLicitacao: function() {
                return {
                    store: this.getStoreGridLicitacao(),
                    controller: 'CPLLicitacao',
                    reload_grid: function(){this.store.reload();}
                };
            },

            getStoreGridLicitacao: function() {
                if(!this.storeGridLicitacao) {
                    this.storeGridLicitacao = new Ext.data.JsonStore({
                        fields: [
                            'codigo',
                            'numero',
                            'dt',
                            'titulo',
                            'interessado',
                            'li_codigo',
                            'li_numero',
                            'li_modalidade',
                            'li_modalidade_pk',
                            'li_data_realizacao',
                            'li_registro_preco',
                            'li_arquivado',
                            'status',
                            'li_contrato',
                            'orcamento'
                        ],
                        root: 'result',
                        totalProperty: 'totalRows',
                        url: toolkit.util.Normalize.controller_action(
                            'CPLGerenciador',
                            'get_store',
                            ['processo']
                        ),
                        remoteSort: true
                    });
                }
                return this.storeGridLicitacao;
            },

            getLicitacaoColumnModel: function() {
                if(!this.licitacaoColumnModel) {
                    this.licitacaoColumnModel = new Ext.grid.ColumnModel([
                        {
                            id: 'status',
                            dataIndex: 'status',
                            header: 'Status',
                            menuDisabled: true,
                            sortable: false,
                            width: 65,
                            renderer: toolkit.util.formatStatus
                        },
                        {dataIndex: 'numero', header: 'Número', sortable: true, width: 120},
                        {dataIndex: 'dt', header: 'Data', sortable: true, width: 70},
                        {dataIndex: 'titulo', header: 'Título', sortable: true, width: 200},
                        {dataIndex: 'interessado', header: 'Interessado', sortable: true, width: 200},
                        {dataIndex: 'li_numero', header: 'LI Número', sortable: true, width: 70},
                        {dataIndex: 'li_modalidade', header: 'Modalidade', sortable: true, width: 120},
                        {dataIndex: 'li_data_realizacao', header: 'Realização', sortable: true, width: 80},
                        {dataIndex: 'li_registro_preco', header: 'Registro de preço', sortable: true, width: 100},
                        {dataIndex: 'li_contrato', header: 'Contrato', sortable: true, width: 100},
                    ]);
                }
                return this.licitacaoColumnModel;
            },

            getLicitacaoGridPaginator: function() {
                if(!this.gridPaginator) {
                    this.gridPaginator = new Ext.PagingToolbar({
                        autoWidth: true,
                        store: this.getStoreGridLicitacao(),
                        displayInfo: true,
                        pageSize: 50,
                        prependButtons: true
                    });
                }
                return this.gridPaginator;
            },

            addLicitacao: function() {
                if(this.getPanelLicitacao().getSelectionModel().getSelected()){
                    new toolkit.adm.cpl.WindowLicitacao({
                        conf_obj: {
                            processo: {
                                codigo: this.getPanelLicitacao().getSelectionModel().getSelected().get('codigo'),
                                numero: this.getPanelLicitacao().getSelectionModel().getSelected().get('numero'),
                                dt: this.getPanelLicitacao().getSelectionModel().getSelected().get('dt'),
                                titulo: this.getPanelLicitacao().getSelectionModel().getSelected().get('titulo'),
                                interessado: this.getPanelLicitacao().getSelectionModel().getSelected().get('interessado'),
                                orcamento: this.getPanelLicitacao().getSelectionModel().getSelected().get('orcamento')
                            }
                        },
                        store: this.getStoreGridLicitacao()}
                    ).show();
                }else alert('Por favor, escolha um Processo!');
            },

            editLicitacao: function() {
                if(this.panelLicitacao.getSelectionModel().getSelected() && this.getPanelLicitacao().getSelectionModel().getSelected().get('li_codigo') != ''){
                    new toolkit.adm.cpl.WindowLicitacao({
                        conf_obj: {
                            processo: {
                                codigo: this.getPanelLicitacao().getSelectionModel().getSelected().get('codigo'),
                                numero: this.getPanelLicitacao().getSelectionModel().getSelected().get('numero'),
                                dt: this.getPanelLicitacao().getSelectionModel().getSelected().get('dt'),
                                titulo: this.getPanelLicitacao().getSelectionModel().getSelected().get('titulo'),
                                interessado: this.getPanelLicitacao().getSelectionModel().getSelected().get('interessado'),
                                orcamento: this.getPanelLicitacao().getSelectionModel().getSelected().get('orcamento')
                            },
                            licitacao: {
                                codigo: this.getPanelLicitacao().getSelectionModel().getSelected().get('li_codigo'),
                                numero: this.getPanelLicitacao().getSelectionModel().getSelected().get('li_numero'),
                                modalidade: this.getPanelLicitacao().getSelectionModel().getSelected().get('li_modalidade_pk'),
                                registro_preco: this.getPanelLicitacao().getSelectionModel().getSelected().get('li_registro_preco'),
                                data_realizacao: this.getPanelLicitacao().getSelectionModel().getSelected().get('li_data_realizacao'),
                                contrato: this.getPanelLicitacao().getSelectionModel().getSelected().get('li_contrato')
                            }
                        },
                        store: this.getStoreGridLicitacao()}
                    ).show();
                }
                else alert('Primeiro selecione um Processo para alterar Licitação.');
            },

            /**
             * Este método realiza o arquivamento de licitações.
             * @param tipo boolean - True, arquiva. False, desfaz arquivamento.
             **/
            arquivarLicitacao: function(tipo) {
                var selection = this.getPanelLicitacao().getSelectionModel();
                if(selection.getSelections()) {
                    Ext.Msg.show({
                        title: 'Arquivar Licitação(ões)',
                        msg: tipo == true ? 'Tem certeza que deseja arquivar Licitações selecionadas (Apenas o(s) Processo(s) com Licitação(ões) serão arquivados)?' : 'Tem certeza que desfazer o arquivamento das Licitações selecionadas?',
                        buttons: Ext.Msg.YESNO,
                        fn: function(bnt) {
                            var ic = [];
                            if(bnt == 'yes') {
                                Ext.each(
                                    selection.getSelections(),
                                    function(record) {ic.push(record.get('li_codigo'));}
                                );

                                Ext.Ajax.request({
                                    url: toolkit.util.Normalize.controller_action(
                                        'CPLGerenciador',
                                        'arquivar'
                                    ),
                                    params: {licitacao: ic, tipo: tipo},
                                    success: function(request) {
                                        var result = Ext.decode(request.responseText);
                                        this.getStoreGridLicitacao().reload();
                                    },
                                    failure: function() {
                                        alert(tipo == true ? 'Ocorreu um erro tentando arquivar as Licitações selecionadas.\nTente novamente mais tarde.' : 'Ocorreu um erro tentando desfazer arquivamento das Licitações selecionadas.\nTente novamente mais tarde.');
                                    },
                                    scope: this
                                });
                            }
                        },
                        icon: Ext.Msg.QUESTION,
                        scope: this
                    });
                }
                else alert(tipo == true ?'Primeiro você deve selecionar as Licitações que deseja arquivar.' : 'Primeiro você deve selecionar as Licitações que deseja desfazer arquivamento.');
            },

            openWindowTab: function(args){
                if(args[2] != undefined){
                    var conf = {
                        aba_set: args[0],
                        tipo: args[1],
                        licitacao: args[2],
                        title: args[3]
                    };
                    switch(args[0]){
                        case participante:new toolkit.adm.cpl.WindowGParticipante(conf).show();break;
                        case vencedor:new toolkit.adm.cpl.WindowGVencedor(conf).show();break;
                        case documento:new toolkit.adm.cpl.WindowGDocumento(conf).show();break;
                        default:alert('Opção não encontrada, tente novamente!');break;
                    }
                }else alert('Primeiro selecione um Processo que possua Licitação!');
            },

            getLicitacaoCodigo: function(){
                if(this.getPanelLicitacao().getSelectionModel().getSelected())
                    return this.getPanelLicitacao().getSelectionModel().getSelected().get('li_codigo');
                return undefined;
            },

            getLicitacaoGridToolbar: function() {
                var menu = [];
                menu.push({
                    text: 'Licitação',
                    iconCls: true,
                    icon: '/' + global.Context + '/static/images/document-sing.png',
                    menu:[
                        {
                            text: 'Incluir',
                            iconCls: true,
                            icon: '/' + global.Context + '/static/engine/images/icons/athenas-0032.png',
                            handler: function(){this.addLicitacao();},
                            scope: this
                        },
                        {
                            text: 'Alterar',
                            iconCls: true,
                            icon: '/' + global.Context + '/static/engine/images/icons/athenas-0034.png',
                            handler: function(){this.editLicitacao();},
                            scope: this
                        }
                    ],
                    scope: this
                });
                menu.push({
                    text: 'Arquivar',
                    iconCls: true,
                    icon: '/' + global.Context + '/static/images/archive.png',
                    scope: this,
                    menu:[
                        {
                            text: 'Sim',
                            iconCls: true,
                            icon: '/' + global.Context + '/static/images/accept.png',
                            handler: function(){this.arquivarLicitacao(true);},
                            scope: this
                        },
                        {
                            text: 'Desfazer arquivamento',
                            iconCls: true,
                            icon: '/' + global.Context + '/static/images/undo-icon.png',
                            handler: function(){this.arquivarLicitacao(false);},
                            scope: this
                        }
                    ]
                });
                menu.push({
                    text: 'Documentos',
                    iconCls: true,
                    icon: '/' + global.Context + '/static/engine/images/icons/athenas-0099.png',
                    handler: function(){this.openWindowTab(['documento', 'documento', this.getLicitacaoCodigo(), 'Gerenciador de Documentos']);},
                    scope: this
                });
                menu.push('-');
                menu.push({
                    text: 'Participante e Vencedor',
                    iconCls: true,
                    icon: '/' + global.Context + '/static/engine/images/icons/athenas-0106.png',
                    handler: function(){this.openWindowTab(['vencedor', 'vencedor', this.getLicitacaoCodigo(), 'Gerenciador de Vencedores']);},
                    scope: this
                });
                return menu;
            }
        }
    );

    /**
     *
     **/
    toolkit.adm.cpl.WindowCustom = Ext.extend(
        Ext.Window,
        {
            constructor: function(cf) {
                if(!cf) cf = {title: 'WindowCustom', closable: true, modal: true};
                toolkit.adm.cpl.WindowCustom.superclass.constructor.call(this, cf);
                this.add(this.getPanelConteiner());
            },

            /**
             * @param args.controller
             * @param args.method
             * @param args.fields
             * @param args.baseParams
             **/
            getStore: function(args){
                if(!this.storeGrid){
                    this.storeGrid = new Ext.data.JsonStore({
                        url: toolkit.util.Normalize.controller_action(
                            args.controller,
                            args.method
                        ),
                        fields: args.fields,
                        root: 'result',
                        totalProperty: 'totalRow',
                        baseParams: args.baseParams,
                        autoLoad: true
                    });
                }
                return this.storeGrid;
            },

            getPanelConteiner: function() {
                if(!this.panelConteiner){
                    this.panelConteiner = new Ext.Panel({
                        layout: 'form',
                        frame: true,
                        border: false,
                        defaults: {width: 365},
                        items: this.getConteinerFields()
                    });
                }
                return this.panelConteiner;
            },

            getConteinerFields: function(){return [];},

            commit: function(args) {
                var form = this.getPanelConteiner().getForm();
                form.waitMsgTarget = this.getEl();
                form.submit({
                    url: toolkit.util.Normalize.controller_action(
                        args.controller,
                        (args.values ? 'update' : 'create')
                    ),
                    params: args.params,
                    validate: 'client',
                    waitMsg: 'Gravando dados...',
                    success: function(form, action) {
                        args.store.reload();
                        if(args.close) this.getPanelConteiner().ownerCt.destroy();
                    },
                    failure: function(form, action) {alert('Falha na gravação dos dados!');},
                    scope: this
                });
            }
        }
    );

    toolkit.adm.cpl.WindowGParticipante = Ext.extend(
        toolkit.adm.cpl.WindowCustom,
        {
            /**
             *  @param conf.aba_set
             *  @param conf.tipo
             *  @param conf.licitacao
             *  @param conf.title
             *
             **/
            constructor: function(conf) {
                var cf = {
                    closable: true,
                    modal: true,
                    layout: 'border',
                    width: 400,
                    height: 200,
                    conf_obj: conf
                };
                toolkit.adm.cpl.WindowGParticipante.superclass.constructor.call(this, cf);
                this.setTitle(this.conf_obj.title);
                this.add(this.getGridParticipante());
            },

            getGridParticipante: function(){
                if(!this.gridParticipante) {
                    this.gridParticipante = new Ext.grid.GridPanel({
                        region: 'center',
                        colModel: new Ext.grid.ColumnModel([
                            {dataIndex: 'codigo', header: 'Código', width: 50, sortable: true},
                            {dataIndex: 'nome', header: 'Nome', width: 370, sortable: true}
                        ]),
                        sm: new Ext.grid.RowSelectionModel({singleSelect: false}),
                        store: this.getStore({controller: 'CPLGerenciador', method: 'get_store/participante', fields: ['codigo','nome'], baseParams: {licitacao: this.conf_obj.licitacao}}),
                        tbar: [
                            {
                                text: 'Adicionar',
                                iconCls: true,
                                icon: '/' + global.Context + '/static/images/add.png',
                                scope: this,
                                handler: this.addParticipante
                            },
                            {
                                text: 'Remover',
                                icon: '/' + global.Context + '/static/images/delete.png',
                                scope: this,
                                handler: this.deleteParticipantes
                            }
                        ],
                        bbar: new Ext.PagingToolbar({
                            store: this.getStore(this.getParamsGrid()),
                            displayInfo: true,
                            pageSize: 50,
                            prependButtons: true
                        })
                    });
                }
                return this.gridParticipante;
            },

            getParamsGrid: function(){
                return {controller: 'CPLGerenciador', method: 'get_store/participante', fields: ['codigo','nome'], baseParams: {}};
            },

            addParticipante: function() {
                this.conf_obj.title = 'Participante';
                new toolkit.adm.cpl.WindowParticipante({conf_obj: this.conf_obj, store: this.getStore(this.getParamsGrid())}).show();
            },

            deleteParticipantes: function() {
                var selection = this.getGridParticipante().getSelectionModel().getSelections();
                if(selection.length > 0) {
                    var pps = [];
                    Ext.each( selection, function(item) {pps.push(item.get('codigo'));});
                    Ext.Msg.show({
                        title: 'Removendo Participantes do processo',
                        msg: 'Tem certeza que deseja remover os Participantes da Licitação?',
                        icon: Ext.Msg.QUESTION,
                        buttons: Ext.Msg.YESNO,
                        fn: function(action) {
                            if(action != 'yes') return;
                            Ext.Ajax.request({
                                url: toolkit.util.Normalize.controller_action(
                                    'CPLGerenciador',
                                    'remove/participante'
                                ),
                                params: {participante: pps, licitacao: this.conf_obj.licitacao},
                                success: function(){this.getStore(this.getParamsGrid()).reload();},
                                scope: this
                            });
                        },
                        scope: this
                    });
                }
                else alert('Primeiro selecione os Participantes que serão removidos.');
            }
        }
    );

    toolkit.adm.cpl.WindowParticipante = Ext.extend(
        toolkit.adm.cpl.WindowCustom,
        {
            constructor: function(conf) {
                var cf = {
                    width: 400,
                    resizable: false,
                    conf_obj: conf.conf_obj,
                    store_father: conf.store
                };
                toolkit.adm.cpl.WindowParticipante.superclass.constructor.call(this, cf);
                this.setTitle(this.conf_obj.title);
                this.add(this.getPanelConteiner());
            },

            getPanelConteiner: function() {
                if(!this.panelConteiner){
                    this.panelConteiner = new Ext.form.FormPanel({
                        frame: true,
                        items: this.getConteinerFields(),
                        buttons: [
                            {text: 'Cancelar', scope: this, handler: this.destroy},
                            {
                                text: 'Salvar',
                                scope: this,
                                handler: function(){
                                    this.commit({
                                        controller: 'CPLGerenciador',
                                        values: undefined,
                                        params: {model: 'participante',licitacao: this.conf_obj.licitacao},
                                        store: this.store_father,
                                        close: false
                                    });
                                }
                            }
                        ]
                    });
                }
                return this.panelConteiner;
            },

            getConteinerFields: function(){
                if(!this.fields){
                    this.fields = [
                        {
                            xtype: 'rest-autocompletefield',
                            fieldLabel: 'Pessoa',
                            allowBlank: true,
                            rest: 'rh.person.Restful',
                            name: 'pessoa',
                            emptyText: 'É necessário preencher este campo.'
                        },
                    ];
                }
                return this.fields;
            }
        }
    );

    toolkit.adm.cpl.WindowLicitacao = Ext.extend(
        toolkit.adm.cpl.WindowCustom,
        {
            constructor: function(conf) {
                var cf = {
                    layout: 'border',
                    width: 400,
                    height: 400,
                    resizable: false,
                    conf_obj: conf.conf_obj,
                    store_father: conf.store
                };
                toolkit.adm.cpl.WindowLicitacao.superclass.constructor.call(this, cf);
                this.setTitle(this.conf_obj.title);
                this.add(this.getPanelConteiner());
                this.add(this.getPanelProcesso());
            },

            getPanelConteiner: function() {
                if(!this.panelConteiner){
                    this.panelConteiner = new Ext.form.FormPanel({
                        title: 'Dados da Licitação',
                        region: 'center',
                        autoHeight: true,
                        animCollapse: true,
                        frame: true,
                        items: this.getConteinerFields(),
                        buttons: [
                            {text: 'Cancelar', scope: this, handler: this.destroy},
                            {
                                text: 'Salvar',
                                scope: this,
                                handler: function(){
                                    var form = this.panelConteiner.getForm();
                                    var values = form.getValues();
                                    this.commit({
                                        controller: 'CPLGerenciador',
                                        values: undefined,
                                        params: {
                                            model: 'licitacao',
                                            licitacao: this.conf_obj.licitacao ? this.conf_obj.licitacao.codigo : ''
                                        },
                                        store: this.store_father,
                                        close: true
                                    });
                                }
                            }
                        ]
                    });
                }
                return this.panelConteiner;
            },

            getConteinerFields: function(){
                if(!this.fields){
                    var contrato = false;
                    var registro_preco = false;
                    if(this.conf_obj.licitacao != undefined){
                        if(this.conf_obj.licitacao.contrato == 'Sim') contrato = true;
                        if(this.conf_obj.licitacao.registro_preco == 'Sim') registro_preco = true;
                    }
                    this.fields = [
                        {
                          displayField: 'description',
                          fieldLabel: 'Processo',
                          allowBlank: false,
                          hiddenName: 'processo',
                          valueField: 'pk',
                          conf: {canAdd: false, canEdit: false},
                          triggerAction: 'all',
                          genericCrud: true,
                          queryAction: 'query',
                          model: {name: 'processoaquisicao', app_label: 'compras'},
                          hideTrigger: true,
                          queryParam: 'keyword',
                          xtype: 'autocompletefield',
                          value: this.conf_obj.processo ? this.conf_obj.processo.codigo : '',
                          editable: false
                        },
                        {
                          fieldLabel: 'Modalidade',
                          xtype: 'combo',
                          hiddenName: 'modalidade',
                          triggerAction: 'all',
                          store: [['', '---------'], [1, 'CONCORR\u00caNCIA'], [2, 'CARTA CONVITE'], [3, 'PREG\u00c3O ELETR\u00d4NICO'], [4, 'PREG\u00c3O PRESENCIAL'], [5, 'TOMADA DE PRE\u00c7O']],
                          allowBlank: false,
                          value: this.conf_obj.licitacao ? this.conf_obj.licitacao.modalidade : ''
                        },
                        {
                          fieldLabel: 'N\u00famero',
                          xtype: 'textfield',
                          name: 'numero',
                          allowBlank: false,
                          value: this.conf_obj.licitacao ? this.conf_obj.licitacao.numero : ''
                        },
                        {
                          allowBlank: true,
                          fieldLabel: 'Data de realiza\u00e7\u00e3o',
                          xtype: 'ndatetimefield',
                          format: 'd/m/Y H:M',
                          name: 'data_realizacao',
                          value: this.conf_obj.licitacao ? this.conf_obj.licitacao.data_realizacao : ''
                        },
                        {
                          fieldLabel: 'Registro de pre\u00e7o',
                          xtype: 'checkbox',
                          name: 'registro_preco',
                          allowBlank: true,
                          checked: registro_preco
                        },
                        {
                          fieldLabel: 'Contrato',
                          xtype: 'checkbox',
                          name: 'contrato',
                          allowBlank: true,
                          checked: contrato
                        }
                    ];
                }
                return this.fields;
            },

            getPanelProcesso: function(){
                if(!this.panelProcesso){
                    this.panelProcesso = new Ext.form.FieldSet({
                        title: 'Dados do Processo',
                        labelWidth: 130,
                        region: 'north',
                        autoHeight: true,
                        animCollapse: true,
                        items: this.getFieldsProcesso()
                    });
                }
                return this.panelProcesso;
            },

            getFieldsProcesso: function(){
                return [
                        {
                            xtype: 'displayfield',
                            fieldLabel: 'Número do Processo',
                            anchor: '100%',
                            name: 'numero',
                            id: 'numero',
                            value: this.conf_obj.processo ? this.conf_obj.processo.numero : ''
                        },
                        {
                            xtype: 'displayfield',
                            fieldLabel: 'Data do Processo',
                            anchor: '100%',
                            name: 'data',
                            id: 'data',
                            value: this.conf_obj.processo ? this.conf_obj.processo.dt : ''
                        },
                        {
                            xtype: 'displayfield',
                            fieldLabel: 'Título',
                            anchor: '100%',
                            name: 'titulo',
                            id: 'titulo',
                            value: this.conf_obj.processo ? this.conf_obj.processo.titulo : ''
                        },
                        {
                            xtype: 'displayfield',
                            fieldLabel: 'Interessado',
                            anchor: '100%',
                            name: 'interessado',
                            id: 'interessado',
                            value: this.conf_obj.processo ? this.conf_obj.processo.interessado : ''
                        },
                        {
                            xtype: 'displayfield',
                            fieldLabel: 'Orçamento',
                            anchor: '100%',
                            name: 'orcamento',
                            id: 'orcamento',
                            value: this.conf_obj.processo ? this.conf_obj.processo.orcamento : ''
                        }
                    ];
            }
        }
    );

    toolkit.adm.cpl.WindowGVencedor = Ext.extend(
        toolkit.adm.cpl.WindowCustom,
        {
            /**
             *  @param conf.aba_set
             *  @param conf.tipo
             *  @param conf.licitacao
             *  @param conf.title
             *
             **/
            constructor: function(conf) {
                var cf = {
                    closable: true,
                    modal: true,
                    resizable: false,
                    layout: 'border',
                    width: 760,
                    minWidth: 760,
                    height: 560,
                    minHeight: 560,
                    conf_obj: conf
                };
                this.storeGrid = {
                    'get_store/participante': undefined,
                    'get_store/produto': undefined,
                    'get_store/vencedorproduto': undefined
                };
                toolkit.adm.cpl.WindowGVencedor.superclass.constructor.call(this, cf);
                this.setTitle(this.conf_obj.title);
                this.add(this.getGridVencedor());
                this.add(this.getPanelProdutos());
            },

            /**
             *  getStore
             *
             * @param args.controller
             * @param args.method
             * @param args.fields
             * @param args.baseParams
             **/
            getStore: function(args){
                if(!this.storeGrid[args.method]){
                    this.storeGrid[args.method] = new Ext.data.JsonStore({
                        url: toolkit.util.Normalize.controller_action(
                            args.controller,
                            args.method
                        ),
                        fields: args.fields,
                        root: 'result',
                        totalProperty: 'totalRow',
                        baseParams: args.baseParams,
                        autoLoad: true
                    });
                }
                return this.storeGrid[args.method];
            },

            getPanelProdutos: function() {
                if(!this.panelConteiner1){
                    this.panelConteiner1 = new Ext.Panel({
                        region: 'south',
                        height: 320,
                        minHeight: 320,
                        maxHeight: 320,
                        layout: 'border',
                        split: true,
                        border: false,
                        items: [
                          this.getPanelCenter(),
                          this.getGridProduto(),
                          this.getGridVencedorProduto()
                        ]
                    });
                }
                return this.panelConteiner1;
            },

            getPanelCenter: function() {
                if(!this.panelCenter){
                    this.panelCenter = new Ext.Panel({
                        region: 'center',
                        width: 20,
                        minWidth: 20,
                        maxWidth: 20,
                        frame: true,
                        border: false,
                        items: [
                            {
                                xtype: 'button',
                                iconCls: true,
                                style: 'margin: 90px 0 5px 0',
                                icon: '/' + global.Context + '/static/adm/images/arrow-right.png',
                                handler: function(){this.addProduto();},
                                scope: this
                            },
                            {
                                xtype: 'button',
                                iconCls: true,
                                style: 'margin: 5px 0',
                                icon: '/' + global.Context + '/static/adm/images/arrow-right-double.png',
                                handler: function(){this.addProdutoAll();},
                                scope: this
                            },
                            {
                                xtype: 'button',
                                iconCls: true,
                                style: 'margin: 5px 0',
                                icon: '/' + global.Context + '/static/adm/images/arrow-left.png',
                                handler: function(){this.remProduto();},
                                scope: this
                            },
                            {
                                xtype: 'button',
                                iconCls: true,
                                style: 'margin: 5px 0',
                                icon: '/' + global.Context + '/static/adm/images/arrow-left-double.png',
                                handler: function(){this.remProdutoAll();},
                                scope: this
                            }
                        ]
                    });
                }
                return this.panelCenter;
            },

            getGridProduto: function(){
                if(!this.gridProduto) {
                    this.gridProduto = new Ext.grid.GridPanel({
                        title: 'Produtos do Processo',
                        region: 'west',
                        width: 350,
                        minWidth: 350,
                        maxWidth: 350,
                        split: true,
                        frame: true,
                        border: false,
                        colModel: new Ext.grid.ColumnModel([
                            {dataIndex: 'nome', header: 'Nome', width: 215, sortable: true},
                            {dataIndex: 'quantidade', header: 'Qtd', width: 40, sortable: true},
                            {dataIndex: 'valor_unitario', header: 'Valor', width: 70, sortable: true, renderer: toolkit.util.formatCurrency},
                            {dataIndex: 'valor_total', header: 'Total', width: 70, sortable: true, renderer: toolkit.util.formatCurrency}
                        ]),
                        sm: new Ext.grid.RowSelectionModel({singleSelect: false}),
                        store: this.getStore({
                            controller: 'CPLGerenciador',
                            method: 'get_store/produto',
                            fields: ['codigo','nome', 'valor_unitario', 'valor_total', 'quantidade'],
                            baseParams: {licitacao: this.conf_obj.licitacao}
                        }),
                        tbar: this.getProdutoGridToolbar()
                    });
                }
                return this.gridProduto;
            },

            getProdutoGridToolbar: function() {
                var menu = [];
                menu.push({
                    text: 'Incluir valor do Lance',
                    iconCls: true,
                    icon: '/' + global.Context + '/static/engine/images/icons/athenas-0572.png',
                    handler: function(){
                        this.conf_obj.title = 'Valor do lance';
                        var wnd = new toolkit.adm.cpl.WindowValorProduto({
                            conf_obj: this.conf_obj,
                            store: this.getStore(this.getParamsGrid({method:'get_store/produto'}))}
                        );
                        wnd.show();
                    },
                    scope: this
                });
                return menu;
            },

            getGridVencedorProduto: function(){
                if(!this.gridVencedorProduto) {
                    this.gridVencedorProduto = new Ext.grid.GridPanel({
                        title: 'Produtos do Vencedor',
                        region: 'east',
                        width: 350,
                        minWidth: 350,
                        maxWidth: 350,
                        split: true,
                        frame: true,
                        border: false,
                        colModel: new Ext.grid.ColumnModel([
                            {dataIndex: 'nome', header: 'Nome', width: 215, sortable: true},
                            {dataIndex: 'quantidade', header: 'Qtd', width: 40, sortable: true},
                            {dataIndex: 'valor_unitario', header: 'Valor', width: 70, sortable: true, renderer: toolkit.util.formatCurrency},
                            {dataIndex: 'valor_total', header: 'Total', width: 70, sortable: true, renderer: toolkit.util.formatCurrency}
                        ]),
                        sm: new Ext.grid.RowSelectionModel({singleSelect: false}),
                        store: this.getStore(this.getParamsGrid({method:'get_store/vencedorproduto'}))
                    });
                }
                return this.gridVencedorProduto;
            },

            getGridVencedor: function(){
                if(!this.gridVencedor) {
                    this.gridVencedor = new Ext.grid.GridPanel({
                        region: 'center',
                        colModel: new Ext.grid.ColumnModel([
                            {
                                id: 'status',
                                dataIndex: 'status',
                                header: 'Status',
                                menuDisabled: true,
                                sortable: false,
                                width: 50,
                                renderer: toolkit.util.formatStatus
                            },
                            {dataIndex: 'nome', header: 'Nome', width: 640, sortable: true}
                        ]),
                        sm: new Ext.grid.RowSelectionModel({
                            singleSelect: false,
                            listeners: {
                                scope: this,
                                rowselect: function(sm) {
                                    this.getGridVencedorProduto().getStore().baseParams.vencedor = this.getVencedor();
                                    this.getGridVencedorProduto().getStore().load();
                                    this.getGridProduto().getStore().load();
                                }
                            }
                        }),
                        store: this.getStore({controller: 'CPLGerenciador', method: 'get_store/participante', fields: ['status','codigo','nome'], baseParams: {licitacao: this.conf_obj.licitacao}}),
                        tbar: [
                            {
                                text: 'Adicionar',
                                iconCls: true,
                                icon: '/' + global.Context + '/static/images/add.png',
                                scope: this,
                                handler: this.addParticipante
                            },
                            {
                                text: 'Remover',
                                icon: '/' + global.Context + '/static/images/delete.png',
                                scope: this,
                                handler: this.remParticipante
                            }
                        ]
                    });
                }
                return this.gridVencedor;
            },

            getParamsGrid: function(args){
                if(args.method == 'get_store/participante')
                    return {controller: 'CPLGerenciador', method: 'get_store/participante', fields: ['status','codigo','nome'], baseParams: {}};
                if(args.method == 'get_store/produto')
                    return {controller: 'CPLGerenciador', method: 'get_store/produto', fields: ['codigo','nome'], baseParams: {}};
                if(args.method == 'get_store/vencedorproduto')
                    return {controller: 'CPLGerenciador', method: 'get_store/vencedorproduto', fields: ['codigo','nome','valor_unitario', 'valor_total', 'quantidade'],
                        baseParams: {vencedor: this.getVencedor(), licitacao: this.conf_obj.licitacao}};
            },

            getVencedor: function(){
                if(this.getGridVencedor().getSelectionModel().getSelected()) return this.getGridVencedor().getSelectionModel().getSelected().get('codigo');
                return undefined;
            },

            manageAction: function(args){
                if(args.validate){
                    if(args.selection.length > 0) {
                        var pps = [];
                        Ext.each( args.selection, function(item) {pps.push(item.get('codigo'));} );
                        args.params.itens = pps;
                        Ext.Ajax.request({
                            url: toolkit.util.Normalize.controller_action(
                                'CPLGerenciador',
                                args.method
                            ),
                            params: args.params,
                            success: function(){
                                this.getStore(this.getParamsGrid({method:'get_store/produto'})).reload();
                                this.getStore(this.getParamsGrid({method:'get_store/vencedorproduto'})).reload();
                                this.getStore(this.getParamsGrid({method:'get_store/participante'})).reload();
                            },
                            scope: this
                        });
                    }else{
                        if((args.method == 'add' || args.method == 'remove') && args.params.model == 'produto')
                            alert('Primeiro selecione o(s) Produto(s).');
                        else if(args.method == 'remove' && args.params.model == 'participante')
                            alert('Primeiro selecione o(s) Vencedore(s).');
                    }
                }else if(!args.params.vencedor) alert('Primeiro selecione o Vencedor.');
            },

            addProduto: function(){
                var params = {itens: [], vencedor: this.getVencedor(), licitacao: this.conf_obj.licitacao, model: 'produto'};
                var args = {method: 'add', validate: this.getVencedor(), selection: this.getGridProduto().getSelectionModel().getSelections(), params: params};
                this.manageAction(args);
            },

            addProdutoAll: function(){
                var params = {itens: [], vencedor: this.getVencedor(), licitacao: this.conf_obj.licitacao, model: 'produto'};
                var args = {method: 'add', validate: this.getVencedor(), selection: this.getGridProduto().store.data.items, params: params};
                this.manageAction(args);
            },

            remProduto: function(){
                var params = {itens: [], vencedor: this.getVencedor(), licitacao: this.conf_obj.licitacao, model: 'produto'};
                var args = {method: 'remove', validate: this.getVencedor(), selection: this.getGridVencedorProduto().getSelectionModel().getSelections(), params: params};
                this.manageAction(args);
            },

            remProdutoAll: function(){
                var params = {itens: [], vencedor: this.getVencedor(), licitacao: this.conf_obj.licitacao, model: 'produto'};
                var args = {method: 'remove', validate: this.getVencedor(), selection: this.getGridVencedorProduto().store.data.items, params: params};
                this.manageAction(args);
            },

            addParticipante: function(){
                this.conf_obj.title = 'Participante';
                new toolkit.adm.cpl.WindowParticipante({conf_obj: this.conf_obj, store: this.getStore(this.getParamsGrid({method:'get_store/participante'}))}).show();
            },

            remParticipante: function(){
                var params = {itens: [], licitacao: this.conf_obj.licitacao, model: 'participante'};
                var args = {method: 'remove', validate: true, selection: this.getGridVencedor().getSelectionModel().getSelections(), params: params};
                this.manageAction(args);
            }
        }
    );

    toolkit.adm.cpl.WindowGDocumento = Ext.extend(
        toolkit.adm.cpl.WindowCustom,
        {
            /**
             *  @param conf.aba_set
             *  @param conf.tipo
             *  @param conf.licitacao
             *  @param conf.title
             *
             **/
            constructor: function(conf) {
                var cf = {
                    closable: true,
                    modal: true,
                    resizable: false,
                    layout: 'border',
                    width: 650,
                    height: 400,
                    conf_obj: conf
                };
                this.storeGrid = {'get_store/documento': undefined};
                toolkit.adm.cpl.WindowGDocumento.superclass.constructor.call(this, cf);
                this.setTitle(this.conf_obj.title);
                this.add(this.getGridDocumento());
            },

            /**
             *  getStore
             *
             * @param args.controller
             * @param args.method
             * @param args.fields
             * @param args.baseParams
             **/
            getStore: function(args){
                if(!this.storeGrid[args.method]){
                    this.storeGrid[args.method] = new Ext.data.JsonStore({
                        url: toolkit.util.Normalize.controller_action(
                            args.controller,
                            args.method
                        ),
                        fields: args.fields,
                        root: 'result',
                        totalProperty: 'totalRow',
                        baseParams: args.baseParams,
                        autoLoad: true
                    });
                }
                return this.storeGrid[args.method];
            },

            getGridDocumento: function(){
                if(!this.gridDocumento) {
                    this.gridDocumento = new Ext.grid.GridPanel({
                        region: 'center',
                        colModel: new Ext.grid.ColumnModel([
                            {dataIndex: 'codigo', header: 'Código', width: 50, sortable: true},
                            {dataIndex: 'tipo', header: 'Tipo', width: 100, sortable: true},
                            {dataIndex: 'natureza', header: 'Natureza', width: 80, sortable: true},
                            {dataIndex: 'data_expedicao', header: 'Expedição', width: 80, sortable: true},
                            {dataIndex: 'data_publicacao', header: 'Data Pub.', width: 80, sortable: true},
                            {dataIndex: 'numero_publicacao', header: 'Número Pub.', width: 80, sortable: true},
                            {dataIndex: 'veiculo_publicacao', header: 'Local Pub.', width: 160, sortable: true}
                        ]),
                        sm: new Ext.grid.RowSelectionModel({singleSelect: false}),
                        store: this.getStore(this.getParamsGrid({method: 'get_store/documento', baseParams: {licitacao: this.conf_obj.licitacao}})),
                        bbar: new Ext.PagingToolbar({
                            store: this.getStore(this.getParamsGrid({method: 'get_store/documento', baseParams: {licitacao: this.conf_obj.licitacao}})),
                            displayInfo: true,
                            pageSize: 50,
                            prependButtons: true
                        }),
                        listeners: {
                            scope: this,
                            dblclick: function() {
                                this.addDocumento([undefined, undefined, this.gridDocumento.getSelectionModel().getSelected()]);
                            }
                        },
                        tbar: [
                            {
                                text: 'Adicionar',
                                iconCls: true,
                                icon: '/' + global.Context + '/static/images/add.png',
                                scope: this,
                                menu:[
                                    {
                                        text: 'Ata de registro de preço',
                                        iconCls: true,
                                        handler: function(){this.addDocumento(['ata_registro','Ata de registro de preço', undefined]);},
                                        scope: this
                                    },
                                    {
                                        text: 'Aviso',
                                        iconCls: true,
                                        handler: function(){this.addDocumento(['aviso','Aviso', undefined]);},
                                        scope: this
                                    },
                                    {
                                        text: 'Edital',
                                        iconCls: true,
                                        handler: function(){this.addDocumento(['edital','Edital', undefined]);},
                                        scope: this
                                    },
                                    {
                                        text: 'Esclarecimento',
                                        iconCls: true,
                                        handler: function(){this.addDocumento(['esclarecimento','Esclarecimento', undefined]);},
                                        scope: this
                                    },
                                    {
                                        text: 'Impugnação',
                                        iconCls: true,
                                        handler: function(){this.addDocumento(['impugnacao','Impugnação', undefined]);},
                                        scope: this
                                    },
                                    {
                                        text: 'Homologação',
                                        iconCls: true,
                                        handler: function(){this.addDocumento(['homologacao','Homologação', undefined]);},
                                        scope: this
                                    }
                                ]
                            },
                            {
                                text: 'Alterar',
                                icon: '/' + global.Context + '/static/images/edit.png',
                                scope: this,
                                handler: function(){
                                    this.addDocumento([undefined, undefined, this.gridDocumento.getSelectionModel().getSelected()]);
                                }
                            },
                            {
                                text: 'Remover',
                                icon: '/' + global.Context + '/static/images/delete.png',
                                scope: this,
                                handler: this.remDocumento
                            }
                        ]
                    });
                }
                return this.gridDocumento;
            },

            getParamsGrid: function(args){
                if(args.method == 'get_store/documento')
                    return {
                        controller: 'CPLGerenciador',
                        method: 'get_store/documento',
                        fields: ['codigo', 'data_expedicao', 'tipo', 'natureza', 'veiculo_publicacao', 'numero_publicacao', 'data_publicacao',
                            'tipo_nome', 'veiculo_publicacao_id', 'arquivo', 'objeto', 'natureza_id'],
                        baseParams: args.baseParams ? args.baseParams : {}
                    };
            },

            manageAction: function(args){
                if(args.validate){
                    if(args.selection.length > 0) {
                        var pps = [];
                        Ext.each( args.selection, function(item) {pps.push(item.get('codigo'));} );
                        args.params.itens = pps;
                        Ext.Ajax.request({
                            url: toolkit.util.Normalize.controller_action(
                                'CPLGerenciador',
                                args.method
                            ),
                            params: args.params,
                            success: function(){
                                store: this.getStore(this.getParamsGrid({method: 'get_store/documento', baseParams: {licitacao: this.conf_obj.licitacao}})).reload();
                            },
                            scope: this
                        });
                    }else{
                        if((args.method == 'add' || args.method == 'remove') && args.params.model == 'produto')
                            alert('Primeiro selecione o(s) Produto(s).');
                        else if(args.method == 'remove' && args.params.model == 'participante')
                            alert('Primeiro selecione o(s) Vencedore(s).');
                    }
                }else if(!args.params.vencedor) alert('Primeiro selecione o Vencedor.');

            },

            addDocumento: function(args){
                this.conf_obj.tipo = args[0];
                this.conf_obj.title = args[1];
                new toolkit.adm.cpl.WindowDocumento({documento: args[2], conf_obj: this.conf_obj, store: this.getStore(this.getParamsGrid({method:'get_store/documento'}))}).show();
            },

            remDocumento: function(){
                var params = {itens: [], licitacao: this.conf_obj.licitacao, model: 'documento'};
                var args = {method: 'remove', validate: true, selection: this.getGridDocumento().getSelectionModel().getSelections(), params: params};
                this.manageAction(args);
            }
        }
    );

    toolkit.adm.cpl.WindowDocumento = Ext.extend(
        toolkit.adm.cpl.WindowCustom,
        {
            constructor: function(conf) {
                var cf = {
                    resizable: false,
                    conf_obj: conf.conf_obj,
                    store_father: conf.store,
                    documento: conf.documento
                };
                toolkit.adm.cpl.WindowDocumento.superclass.constructor.call(this, cf);
                this.setTitle(this.documento ? this.documento.get('tipo') : this.conf_obj.title);
                this.add(this.getPanelConteiner());
            },

            getValueTipo: function(value){
                switch(value){
                    case ata_registro:return 1;
                    case aviso:return 2;
                    case edital:return 3;
                    case esclarecimento:return 4;
                    case impugnacao:return 5;
                    case homologacao:return 6;
                }
            },

            getPanelConteiner: function() {
                if(!this.panelConteiner){
                    this.panelConteiner = new Ext.form.FormPanel({
                        frame: true,
                        items: this.getConteinerFields(),
                        buttons: [
                            {text: 'Cancelar', scope: this, handler: this.destroy},
                            {
                                text: 'Salvar',
                                scope: this,
                                handler: function(){
                                    this.commit({
                                        controller: 'CPLGerenciador',
                                        values: undefined,
                                        params: {
                                            documento: this.documento ? this.documento.get('codigo') : undefined,
                                            model: 'documento',
                                            licitacao: this.conf_obj.licitacao,
                                            tipo: this.getValueTipo(this.conf_obj.tipo)
                                        },
                                        store: this.store_father,
                                        close: true
                                    });
                                }
                            }
                        ]
                    });
                }
                return this.panelConteiner;
            },

            getConteinerFields: function(){
                var fields = [];
                this.conf_obj.tipo = this.documento ? this.documento.get('tipo_nome') : this.conf_obj.tipo;
                if(this.conf_obj.tipo == 'aviso' || this.conf_obj.tipo == 'edital'){
                    fields.push({
                        hiddenName: 'natureza',
                        fieldLabel: 'Natureza',
                        xtype: 'combo',
                        allowBlank: true,
                        validateOnBlur: true,
                        blankText: 'É necessário preencher este campo.',
                        store: [['', '---------'], [1, 'ADIADO'], [2, 'PRORROGADO'], [3, 'REMARCADO']],
                        displayField: 'description',
                        typeAhead: true,
                        mode: 'local',
                        triggerAction: 'all',
                        emptyText:'Selecione um item...',
                        selectOnFocus:true,
                        editable: true,
                        value: this.documento ? this.documento.get('natureza_id') : '',
                        listeners: {
                            scope: this,
                            select: function(combo, record, index){
                                if(index > 0) this.getPanelConteiner().getForm().findField('data_realizacao').enable();
                                else this.getPanelConteiner().getForm().findField('data_realizacao').disable();
                            }
                        }
                    });
                }
                if(this.conf_obj.tipo == 'edital')
                    fields.push({
                        disabled: false,
                        name: 'data_realizacao',
                        fieldLabel: 'Data de Realização',
                        xtype: 'datefield',
                        allowBlank: true,
                        validateOnBlur: true,
                        blankText: 'É necessário preencher este campo.',
                        value: this.documento ? this.documento.get('data_realizacao') : ''
                    });
                fields.push({
                    name: 'arquivo',
                    fieldLabel: 'Arquivo',
                    xtype: 'ged-fileuploadfield',
                    allowBlank: true,
                    validateOnBlur: true,
                    blankText: 'É necessário preencher este campo.',
                    value: this.documento ? this.documento.get('arquivo') : ''
                });
                fields.push({
                    name: 'data_expedicao',
                    fieldLabel: 'Data de expedição',
                    xtype: 'datefield',
                    allowBlank: true,
                    validateOnBlur: true,
                    blankText: 'É necessário preencher este campo.',
                    value: this.documento ? this.documento.get('data_expedicao') : ''
                });
                fields.push({
                    name: 'objeto',
                    fieldLabel: 'Objeto',
                    xtype: 'xhtmleditor',
                    height: 175,
                    allowBlank: true,
                    validateOnBlur: true,
                    blankText: 'É necessário preencher este campo.',
                    value: this.documento ? this.documento.get('objeto') : ''
                });
                if(this.conf_obj.tipo != 'edital'){
                    fields.push({
                        hiddenName: 'veiculo_publicacao',
                        fieldLabel: 'Veículo Publicação',
                        xtype: 'combo',
                        allowBlank: true,
                        validateOnBlur: true,
                        blankText: 'É necessário preencher este campo.',
                        store: [['', '---------'], [0, 'DI\u00c1RIO OFICIAL DA UNI\u00c3O'], [28, 'DI\u00c1RIO DA JUSTI\u00c7A'], [29, 'DI\u00c1RIO DA JUSTI\u00c7A ELEITORAL'], [1, 'DI\u00c1RIO OFICIAL DO ESTADO ACRE'], [2, 'DI\u00c1RIO OFICIAL DO ESTADO AMAP\u00c1'], [3, 'DI\u00c1RIO OFICIAL DO ESTADO AMAZONAS'], [13, 'DI\u00c1RIO OFICIAL DO ESTADO BAHIA'], [8, 'DI\u00c1RIO OFICIAL DO ESTADO CEAR\u00c1'], [26, 'DI\u00c1RIO OFICIAL DO ESTADO DISTRITO FEDERAL'], [18, 'DI\u00c1RIO OFICIAL DO ESTADO ESP\u00cdRITO SANTO'], [25, 'DI\u00c1RIO OFICIAL DO ESTADO GOI\u00c1S'], [6, 'DI\u00c1RIO OFICIAL DO ESTADO PAR\u00c1'], [21, 'DI\u00c1RIO OFICIAL DO ESTADO PARAN\u00c1'], [11, 'DI\u00c1RIO OFICIAL DO ESTADO PARA\u00cdBA'], [10, 'DI\u00c1RIO OFICIAL DO ESTADO PERNAMBUCO'], [15, 'DI\u00c1RIO OFICIAL DO ESTADO PIAU\u00cd'], [27, 'DI\u00c1RIO OFICIAL DO ESTADO MATO GROSSO'], [24, 'DI\u00c1RIO OFICIAL DO ESTADO MATO GROSSO DO SUL'], [14, 'DI\u00c1RIO OFICIAL DO ESTADO MARANH\u00c3O'], [16, 'DI\u00c1RIO OFICIAL DO ESTADO MINAS GERAIS'], [19, 'DI\u00c1RIO OFICIAL DO ESTADO RIO DE JANEIRO'], [9, 'DI\u00c1RIO OFICIAL DO ESTADO RIO GRANDE DO NORTE'], [23, 'DI\u00c1RIO OFICIAL DO ESTADO RIO GRANDE DO SUL'], [4, 'DI\u00c1RIO OFICIAL DO ESTADO RORAIMA'], [5, 'DI\u00c1RIO OFICIAL DO ESTADO ROND\u00d4NIA'], [22, 'DI\u00c1RIO OFICIAL DO ESTADO SANTA CATARINA'], [17, 'DI\u00c1RIO OFICIAL DO ESTADO S\u00c3O PAULO'], [12, 'DI\u00c1RIO OFICIAL DO ESTADO SERGIPE'], [7, 'DI\u00c1RIO OFICIAL DO ESTADO TOCANTINS']],
                        displayField: 'description',
                        typeAhead: true,
                        mode: 'local',
                        triggerAction: 'all',
                        emptyText:'Selecione um item...',
                        selectOnFocus:true,
                        editable: true,
                        value: this.documento ? this.documento.get('veiculo_publicacao_id') : ''
                    });
                    fields.push({
                        name: 'numero_publicacao',
                        fieldLabel: 'Número Publicação',
                        xtype: 'textfield',
                        allowBlank: true,
                        validateOnBlur: true,
                        blankText: 'É necessário preencher este campo.',
                        value: this.documento ? this.documento.get('numero_publicacao') : ''
                    });
                    fields.push({
                        name: 'data_publicacao',
                        fieldLabel: 'Data da Publicação',
                        xtype: 'datefield',
                        allowBlank: true,
                        validateOnBlur: true,
                        blankText: 'É necessário preencher este campo.',
                        value: this.documento ? this.documento.get('data_publicacao') : ''
                    });
                }
                return fields;
            }
        }
    );

    toolkit.adm.cpl.WindowValorProduto = Ext.extend(
        toolkit.adm.cpl.WindowCustom,
        {
            constructor: function(conf) {
                var cf = {
                    resizable: false,
                    conf_obj: conf.conf_obj,
                    store_father: conf.store,
                    documento: conf.documento,
                    width: 400,
                    height: 400
                };
                toolkit.adm.cpl.WindowValorProduto.superclass.constructor.call(this, cf);
                this.setTitle(this.conf_obj.title);
                this.add(this.getPanelConteiner());
                this.on('render', function() {this.getStoreProd().load();},this);
            },

            getPanelConteiner: function() {
                if(!this.panelConteiner){
                    this.panelConteiner = this.getConteinerFields();
                }
                return this.panelConteiner;
            },

            getProduto: function(){
                if(this.produto == undefined){
                    this.produto = Ext.data.Record.create([
                        {name: 'codigo'},
                        {name: 'nome',type: 'string'},
                        {name: 'valor_unitario_estimado',/*type: 'string',*/ renderer: toolkit.util.formatCurrency},
                        {name: 'valor_unitario_lance',/*type: 'string',*/ renderer: toolkit.util.formatCurrency},
                        {name: 'valor_unitario_aditivo',/*type: 'string',*/ renderer: toolkit.util.formatCurrency}
                    ]);
                }
                return this.produto;
            },

            getReader: function(){
                if(this.reader == undefined){
                    this.reader = new Ext.data.JsonReader({
                            totalProperty: 'totalRows',
                            successProperty: 'success',
                            root: 'result',
                            start: 0,
                            limit: 50
                        },
                    this.getProduto());
                }
                return this.reader;
            },

            getProxy:function(){
                if(this.proxy == undefined){
                    this.proxy = new Ext.data.HttpProxy({
                        api: {
                            read: 'CPLGerenciador/get_store/produto/',
                            create: 'CPLGerenciador/update/produto/',
                            update: 'CPLGerenciador/update/produto/',
                            destroy: 'CPLGerenciador/get_store/produto/destroy/'
                        }
                    });
                }
                return this.proxy;
            },

            getWriter: function(){
                if(this.writer == undefined){
                    this.writer = new Ext.data.JsonWriter({
                        encode: true,
                        writeAllFields: false
                    });
                }
                return this.writer;
            },

            getStoreProd: function(){
                if(this.storeProd == undefined){
                    this.storeProd = new Ext.data.Store({
                        id: 'user',
                        proxy: this.getProxy(),
                        reader: this.getReader(),
                        writer: this.getWriter(),  // <-- plug a DataWriter into the store just as you would a Reader
                        autoSave: false, // <-- false would delay executing create, update, destroy requests until specifically told to do so with some [save] buton.
                        baseParams:{start: 0, limit: 50, licitacao: this.conf_obj.licitacao},
                        listeners: {
                            scope: this,
                            update: function(store, record, operation ){
                                store.save();
                                store.reload();
                                this.store_father.reload();
                            }
                        }
                    });
                }
                return this.storeProd;
            },

            getConteinerFields: function(){

                if(this.grid == undefined){
                    this.grid = new Ext.grid.EditorGridPanel({
                        clicksToEdit: 1,
                        height: 370,
                        store: this.getStoreProd(),
                        columns: [
                            {
                                dataIndex: 'nome',
                                header: 'Produto',
                                width: 220,
                                sortable: true
                            },
                            {
                                dataIndex: 'valor_unitario_estimado',
                                header: 'Valor estimado',
                                width: 100,
                                sortable: true,
                                editor:{xtype:'textfield',allowBlank: false},
                                renderer: toolkit.util.formatCurrency
                            },
                            {
                                dataIndex: 'valor_unitario_lance',
                                header: 'Valor lance',
                                width: 65,
                                sortable: true,
                                editor:{xtype:'textfield',allowBlank: false},
                                renderer: toolkit.util.formatCurrency
                            }
                        ],
                        tbar: [
                            {
                                iconCls: 'icon-user-save',
                                text: 'Salvar modificações',
                                handler:function(){this.getStoreProd().save();},
                                scope: this
                            }
                        ],
                        bbar: new Ext.PagingToolbar({
                            autoWidth: true,
                            store: this.getStoreProd(),
                            displayInfo: true,
                            pageSize: 50,
                            prependButtons: true
                        })
                    });
                }
                return this.grid;
            }
        }
    );

}
