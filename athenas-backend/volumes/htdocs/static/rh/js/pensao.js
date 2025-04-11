if(typeof(toolkit.rh.pensao) == 'undefined') {
    Ext.ns('toolkit.rh.pensao');

    toolkit.rh.pensao.Gerenciador = Ext.extend(
        Ext.Panel,
        {
            constructor: function() {
                var cf = {
                    title: 'Pensões',
                    closable: true,
                    layout: 'border',
                    border: false
                };

                this.store = {
                    'store/servidor': undefined,
                    'store/pensao': undefined,
                    'store/evento': undefined
                }

                this.servidor = undefined;

                toolkit.rh.pensao.Gerenciador.superclass.constructor.call(this, cf);

                var active = toolkit.Application.tabspace.getActiveTab();
                toolkit.Application.tabspace.remove(active);
                toolkit.Application.tabspace.add(this);
                
                this.add(this.getGridServidor());
                this.add(this.getPensoes());
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
                if(!this.store[args.method]){
                    this.store[args.method] = new Ext.data.JsonStore({
                        url: toolkit.util.Normalize.controller_action(
                            args.controller,
                            args.method
                        ),
                        fields: args.fields,
                        root: 'result',
                        totalProperty: 'totalRows',
                        baseParams: args.baseParams,
                        autoLoad: args.auto ? args.auto : false
                    });
                }
                return this.store[args.method];
            },

            getParamsGrid: function(args){
                if(args.method == 'store/servidor')
                    return {
                        controller: 'PENSAOGerenciadorPensao', 
                        method: 'store/servidor', 
                        fields: [
                            'status',
                            'codigo',
                            'descricao'
                        ], 
                        baseParams: {}, 
                        auto: true
                    };
                if(args.method == 'store/pensao')
                    return {
                        controller: 'PENSAOGerenciadorPensao', 
                        method: 'store/pensao', 
                        fields: [
                            'status',
                            'codigo',
                            'descricao', 
                            'pensionista', 
                            'publicacao', 
                            'dedutivel_irrf', 
                            'tipo'
                        ],
                        baseParams:  {servidor: ''}, 
                        auto: false
                    };
                if(args.method == 'store/evento')
                    return {
                        controller: 'PENSAOGerenciadorPensao', 
                        method: 'store/evento', 
                        fields: [
                            'codigo',
                            'descricao',
                            'valor',
                        ], 
                        baseParams: args.baseParams, 
                        auto: false
                    };
            },

            getGridServidor: function(){
                if(!this.gridServidor) {
                    this.gridServidor = new Ext.grid.GridPanel({
                        region: 'center',
                        border: true,
                        bodyStyle: 'border-left:none;border-top:none;border-right:none',
                        autoExpandColumn: 'autoExpandId',
                        cm: new Ext.grid.ColumnModel([
                            {
                                id: 'status',
                                dataIndex: 'status',
                                header: '',
                                menuDisabled: true,
                                sortable: false,
                                width: 25,
                                renderer: toolkit.util.formatStatus
                            },
                            {
                                dataIndex: 'descricao', 
                                header: 'Servidor', 
                                width: 550, 
                                sortable: true,
                                id: 'autoExpandId'
                            }
                        ]),
                        sm: new Ext.grid.RowSelectionModel({
                            singleSelect: false,
                            listeners: {
                                scope: this,
                                rowselect: function(sm) {
                                    this.getGridPensao().getStore().baseParams.servidor = sm.getSelected().get('codigo');
                                    this.getGridEvento().getStore().baseParams = [];
                                    this.getGridPensao().getStore().load();
                                    this.getGridEvento().getStore().load();
                                }
                            }
                        }),
                        store: this.getStore(this.getParamsGrid({method: 'store/servidor'})),
                        tbar:[
                            {
                                text: 'Pensões',
                                iconCls: true,
                                icon: '/' + global.Context + '/static/images/add.png',
                                scope: this,
                                menu: [
                                    {
                                        text: "Pensão Alimentícia",
                                        iconCls: true,
                                        icon: "/" + global.Context + "/static/rh/images/pensaoalimenticia.png",
                                        handler: function(){
                                            new toolkit.widget.ExtCrudForm(
                                                this.getFatherPensaoServidor('pensaoalimenticia'),
                                                toolkit.widget.ExtCrudForm.TYPE.NEW,
                                                false,
                                                []
                                            ).show();
                                        },
                                        scope: this
                                    },
                                    {
                                        text: "Pensão por Morte",
                                        iconCls: true,
                                        icon: "/" + global.Context + "/static/rh/images/pensaomorte.png",
                                        handler: function(){
                                            new toolkit.widget.ExtCrudForm(
                                                this.getFatherPensaoServidor('pensaomorte'),
                                                toolkit.widget.ExtCrudForm.TYPE.NEW,
                                                false,
                                                []
                                            ).show();
                                        },
                                        scope: this
                                    }
                                ]
                            },
                            {
                                text: 'Remover',
                                iconCls: true,
                                icon: '/' + global.Context + '/static/images/delete.png',
                                scope: this,
                                handler: function(){
                                    if(confirm("Este procedimento apagará todas pensões do servidor!Você deseja realizar este procedimento?")){
                                        var servidor = [];
                                        Ext.each( this.getGridServidor().getSelectionModel().getSelections(), function(item) {servidor.push(item.get('codigo'));} );
                                        this.remover('servidor', servidor, 
                                            function(owner){
                                                owner.getGridServidor().getStore().load();
                                                owner.getGridPensao().getStore().load();
                                                owner.getGridEvento().getStore().load();
                                            }
                                        );
                                    }
                                }
                            }
                        ],
                        bbar: new Ext.PagingToolbar({
                            autoWidth: true,
                            store: this.getStore(this.getParamsGrid({method: 'store/servidor'})),
                            displayInfo: true,
                            pageSize: 50,
                            prependButtons: true,
                            border: false
                        })
                    });
                }
                return this.gridServidor;
            },

            remover: function(model, selected, store) {
                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('PENSAOGerenciadorPensao', 'remover'),
                    params: {model: model, selected: selected},
                    success: function(request){ store(this) },
                    failure: function() {alert('Ocorreu um erro tentando copiar eventos.');},
                    scope: this
                });
            },

            getServidorCodigo: function(){
                if(this.getGridServidor().getSelectionModel().getSelected())
                    return this.getGridServidor().getSelectionModel().getSelected().get('codigo');
                return undefined;
            },

            getPensoes: function() {
                if(!this.panelConteiner1){
                    this.panelConteiner1 = new Ext.Panel({
                        region: 'south',
                        height: 235,
//                        minHeight: 235,
//                        maxHeight: 435,
                        layout: 'border',
                        split: true,
                        border: false,
                        items: [ this.getGridPensao(), this.getGridEvento() ]
                    });
                }
                return this.panelConteiner1;
            },

            getGridPensao: function(){
                if(!this.gridPensao) {
                    this.gridPensao = new Ext.grid.GridPanel({
//                         title: 'Beneficiários',
                        region: 'center',
                        split: true,
                        border: true,
                        bodyStyle: 'border-left:none',
                        headerStyle: 'border-left:none',
                        sm: new Ext.grid.RowSelectionModel({
                            singleSelect: false,
                            listeners: {
                                scope: this,
                                rowselect: function(sm) {
                                    this.getGridEvento().getStore().baseParams.pensao = sm.getSelected().get('codigo');
                                    this.getGridEvento().getStore().load();
                                }
                            }
                        }),
                        autoExpandColumn: 'autoExpandId',
                        cm: new Ext.grid.ColumnModel([
                            {
                                id: 'status',
                                dataIndex: 'status',
                                header: '',
                                menuDisabled: true,
                                sortable: false,
                                width: 25,
                                renderer: toolkit.util.formatStatus
                            },
                            {
                                dataIndex: 'descricao', 
                                header: 'Beneficiário', 
                                width: 260, 
                                sortable: true, 
                                id: 'autoExpandId',
                                menuDisabled: true
                            },
//                             {dataIndex: 'publicacao', header: 'Publicação', width: 250, sortable: true},
                            {
                                dataIndex: 'dedutivel_irrf', 
                                header: 'IRRF', 
                                width: 80, 
                                sortable: true,
                                menuDisabled: true
                            }
                        ]),
                        listeners:{
                            scope: this,
                            dblclick: function() {
                                this.editPensao(this.getGridPensao().getSelectionModel().getSelected().get("tipo"));
                            }
                        },
                        store: this.getStore(this.getParamsGrid({method: 'store/pensao'})),
                        tbar: this.getTbarServidorPensao(),
                        bbar: new Ext.PagingToolbar({
                            autoWidth: true,
                            store: this.getStore(this.getParamsGrid({method: 'store/pensao'})),
                            displayInfo: true,
                            pageSize: 50,
                            prependButtons: true
                        })
                    });
                }
                return this.gridPensao;
            },

            getPensaoId:function(){
                if(this.getGridPensao().getSelectionModel().getSelected())
                    return this.getGridPensao().getSelectionModel().getSelected().get("codigo");
                return undefined;
            },

            getTipo:function(){
                if(this.getGridPensao().getSelectionModel().getSelected())
                    return this.getGridPensao().getSelectionModel().getSelected().get("tipo");
                return undefined
            },

            getTbarServidorPensao: function(){
                if(this.tbarServidorPensao == undefined)
                    this.tbarServidorPensao = [
                        {
                            text: 'Pensões',
                            iconCls: true,
                            icon: '/' + global.Context + '/static/images/add.png',
                            scope: this,
                            menu: [
                                {
                                    text: "Pensão Alimentícia",
                                    iconCls: true,
                                    icon: "/" + global.Context + "/static/rh/images/pensaoalimenticia.png",
                                    handler: function(){this.addPensao('pensaoalimenticia')},
                                    scope: this
                                },
                                {
                                    text: "Pensão por morte",
                                    iconCls: true,
                                    icon: "/" + global.Context + "/static/rh/images/pensaomorte.png",
                                    handler: function(){this.addPensao('pensaomorte')},
                                    scope: this
                                }
                            ]
                        },
                        {
                            text: 'Copiar eventos de',
                            iconCls: true,
                            icon: '/' + global.Context + '/static/images/add.png',
                            scope: this,
                            handler: function(){
                                var evento = [];
                                Ext.each( this.getGridEvento().getSelectionModel().getSelections(), function(item) {evento.push(item.get('codigo'));} );
                                if(evento.length > 0 && this.getServidorCodigo())
                                    new toolkit.rh.pensao.CopiarPensao({
                                        servidor: this.getServidorCodigo(),
                                        pensao: this.getPensaoId(),
                                        evento: evento,
                                        store: this.getStore(this.getParamsGrid({method: 'store/pensao'})),
                                        tipo: this.getGridPensao().getSelectionModel().getSelected().get("tipo")
                                    }).show();
                                else alert('Escolha o servidor e o(s) evento(s)!')
                            }
                        },
                        {
                            text: 'Remover',
                            iconCls: true,
                            icon: '/' + global.Context + '/static/images/delete.png',
                            scope: this,
                            handler: function(){
                                if(confirm("Este procedimento apagará todas pensões do servidor!Você deseja realizar este procedimento?")){
                                    var pensao = [];
                                    Ext.each( this.getGridPensao().getSelectionModel().getSelections(), function(item) {pensao.push(item.get('codigo'));} );
                                    this.remover('pensao', pensao,
                                        function(owner){
                                            owner.getGridServidor().getStore().load();
                                            owner.getGridPensao().getStore().load();
                                            owner.getGridEvento().getStore().load();
                                        }
                                    );
                                }
                            }
                        }
                    ];
                return this.tbarServidorPensao;
            },

            addPensao: function(type) {
                new toolkit.widget.ExtCrudForm(
                    this.getFatherPensao(type),
                    toolkit.widget.ExtCrudForm.TYPE.NEW,
                    false,
                    this.getServidorCodigo() ? [{value: this.getServidorCodigo(), name: "servidor", enabled: false}] : []
                ).show();
            },

            editPensao: function(type) {
                if(this.verificaPensao())
                    new toolkit.widget.ExtCrudForm(
                        this.getFatherPensao(type),
                        toolkit.widget.ExtCrudForm.TYPE.EDIT,
                        this.getPensaoId(),
                        this.getServidorCodigo() ? [{servidor: this.getServidorCodigo(), name: "servidor", enabled: false}] : []
                    ).show();
            },

            getFatherPensao: function(tipo) {
                var father = false;
                var dict = {
                    'pensaoalimenticia': 'PENSAOPensaoAlimenticia',
                    'pensaomorte': 'PENSAOPensaoMorte'
                }
                father = {
                    store: this.getStore(this.getParamsGrid({method: 'store/pensao'})),
                    controller: dict[tipo],
                    reload_grid: function(){
                        this.store.reload();
                    }
                };
                return father;
            },

            getFatherPensaoServidor: function(tipo) {
                var father = false;
                var dict = {
                    'pensaoalimenticia': 'PENSAOPensaoAlimenticia',
                    'pensaomorte': 'PENSAOPensaoMorte'
                }
                father = {
                    store: this.getStore(this.getParamsGrid({method: 'store/servidor'})),
                    controller: dict[tipo],
                    reload_grid: function(){
                        this.store.reload();
                    }
                };
                return father;
            },

            getGridEvento: function(){
                if(!this.gridEvento) {
                    this.gridEvento = new Ext.grid.GridPanel({
//                         title: 'Eventos de cada pensão',
                        region: 'east',
                        width: 400,
                        minWidth: 300,
                        maxWidth: 300,
                        split: true,
                        border: true,
                        bodyStyle: 'border-right:none',
                        headerStyle: 'border-right:none',
                        autoExpandColumn: 'autoExpandId',
                        colModel: new Ext.grid.ColumnModel([
                            {
                                dataIndex: 'descricao', 
                                header: 'Evento', 
                                width: 150, 
                                sortable: true, 
                                id: 'autoExpandId'
                            },
                            {
                                dataIndex: 'valor', 
                                header: 'Valor', 
                                width: 80, 
                                sortable: true, 
                                menuDisabled: true,
                                renderer: function(value) {
                                    var tpl = new Ext.XTemplate(
                                        '<p style="text-align:center">',
                                            '<tpl if="tipo == 1">',
                                                'R$ {valor}',
                                            '</tpl>',
                                            '<tpl if="tipo == 2">',
                                                '{valor} %',
                                            '</tpl>',
                                            '<tpl if="tipo == 3">',
                                                '{valor}',
                                            '</tpl>',
                                        '</p>'
                                    );
                                    
                                    value.valor = Ext.util.Format.number(value.valor, '0.0,0000/i');
                                    
                                    return tpl.apply(value);
                                }
                            },
                        ]),
                        sm: new Ext.grid.RowSelectionModel({singleSelect: false}),
                        store: this.getStore(this.getParamsGrid({method:'store/evento', baseParams: {pensao: this.getPensaoId()}})),
                        tbar: [
                            {
                                text: 'Adicionar',
                                iconCls: true,
                                icon: '/' + global.Context + '/static/images/add.png',
                                scope: this,
                                handler: function(){this.addEvento(this.getTipo())}
                            },
                            ('-'),
                            {
                                text: 'Editar',
                                iconCls: true,
                                icon: '/' + global.Context + '/static/images/edit.png',
                                scope: this,
                                handler: function(){this.editEvento(this.getTipo())}
                            },
                            ('-'),
                            {
                                text: 'Remover',
                                iconCls: true,
                                icon: '/' + global.Context + '/static/images/delete.png',
                                scope: this,
                                handler: function(){this.deleteEvento(this.getTipo())}
                            }
                        ],
                        bbar: new Ext.PagingToolbar({
                            autoWidth: true,
                            store: this.getStore(this.getParamsGrid({method: 'store/evento'})),
                            displayInfo: true,
                            pageSize: 50,
                            prependButtons: true
                        }),
                        listeners:{
                            scope: this,
                            dblclick: function() {
                                this.editEvento(this.getTipo());
                            }
                        }
                    });
                }
                return this.gridEvento;
            },

            getEvento: function(){
                if(this.getGridEvento().getSelectionModel().getSelected())
                    return this.getGridEvento().getSelectionModel().getSelected().get("codigo");
                return undefined;
            },

            verificaPensao: function(){
                if(!this.getPensaoId()){
                    alert('Escolha uma pensão!');
                    return false;
                }
                return true;
            },
            
            verificaEvento: function(){
                if(!this.getEvento()){
                    alert('Escolha um Evento!');
                    return false;
                }
                return true;
            },

            verificaServidor: function(){
                if(!this.getServidorCodigo()){
                    alert('Escolha um Servidor!');
                    return false;
                }
                return true;
            },

            addEvento: function(type) {
                if(this.verificaPensao())
                    new toolkit.widget.ExtCrudForm(
                        this.getFatherPensaoEvento(type),
                        toolkit.widget.ExtCrudForm.TYPE.NEW,
                        false,
                        this.getPensaoId() ? [{value: this.getPensaoId(), name: type == 'pensaoalimenticia' ? "pensao_alimenticia" : "pensao_morte",enabled: false}] : []
                    ).show();
            },

            editEvento: function(type) {
                if(this.verificaPensao() && this.verificaEvento())
                    new toolkit.widget.ExtCrudForm(
                        this.getFatherPensaoEvento(type),
                        toolkit.widget.ExtCrudForm.TYPE.EDIT,
                        this.getEvento(),
                        this.getPensaoId() ? [{value: this.getPensaoId(), name: type == 'pensaoalimenticia' ? "pensao_alimenticia" : "pensao_morte",enabled: false}] : []
                    ).show();
            },

            deleteEvento: function(){
                if(this.getGridEvento().getSelectionModel().getSelections().length > 0) {
                    var evento = [];
                    Ext.each( this.getGridEvento().getSelectionModel().getSelections(), function(item) {evento.push(item.get('codigo'));} );
                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action(
                            'PENSAOGerenciadorPensao',
                            'remover'
                        ),
                        params: {evento: evento, tipo: this.getTipo(), pensao: this.getPensaoId()},
                        success: function(){
                            store: this.getStore(this.getParamsGrid({method: 'store/evento', baseParams: {pensao: this.getPensaoId()}})).reload();
                        },
                        scope: this
                    });
                }else alert('Selecione o(s) evento(s)!')
            },

            getFatherPensaoEvento: function(tipo) {
                var father = false;
                var dict = {
                    'pensaoalimenticia': 'PENSAOPensaoAlimenticiaEvento',
                    'pensaomorte': 'PENSAOPensaoMorteEvento'
                }
                father = {
                    store: this.getStore(this.getParamsGrid({method: 'store/evento'})),
                    controller: dict[tipo],
                    reload_grid: function(){
                        this.store.reload();
                    }
                };
                return father;
            }

        }
    );

    toolkit.rh.pensao.CopiarPensao = Ext.extend(
        Ext.Window,
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
                    title: 'Copiando eventos para...',
                    closable: true,
                    modal: true,
                    layout: 'border',
                    width: 400,
                    height: 200,
                    conf_obj: conf,
                    buttons:[
                        {text: 'Cancelar', scope: this, handler: this.destroy},
                        {
                            text: 'Salvar',
                            scope: this,
                            handler: function(){
                                if(this.getPensao().getSelectionModel().getSelections()){
                                    var pensao = [];
                                    Ext.each( this.getPensao().getSelectionModel().getSelections(), function(item) {pensao.push(item.get('codigo'));} );
                                    this.copiar(pensao, this.conf_obj.evento);
                                }else alert('Escolha pelo menos um!');
                            }
                        }
                    ]
                }
                toolkit.rh.pensao.CopiarPensao.superclass.constructor.call(this, cf);
                this.add(this.getPensao());
                var obj = this;
                setTimeout(function() {obj.doLayout();}, 50);
                this.getStore().baseParams.servidor = this.conf_obj.servidor;
                this.getStore().baseParams.pensao = this.conf_obj.pensao;
                this.on('render', function() {this.getStore().load({params:{start: 0, limit: 50}});},this);
            },

            getPensao: function(){
                if(!this.gridPensao) {
                    this.gridPensao = new Ext.grid.GridPanel({
                        region: 'center',
                        sm: new Ext.grid.RowSelectionModel({singleSelect: false}),
                        colModel: new Ext.grid.ColumnModel([
                            {
                                id: 'status',
                                dataIndex: 'status',
                                header: '',
                                menuDisabled: true,
                                sortable: false,
                                width: 25,
                                renderer: toolkit.util.formatStatus
                            },
                            {dataIndex: 'descricao', header: 'Descrição', width: 300, sortable: true}
                        ]),
                        store: this.getStore()
                    });
                }
                return this.gridPensao;
            },

            getStore: function(){
                if(!this.store){
                    this.store = new Ext.data.JsonStore({
                        url: toolkit.util.Normalize.controller_action(
                            'PENSAOGerenciadorPensao',
                            'store/pensao'
                        ),
                        fields: ['status','codigo','descricao', 'pensionista', 'publicacao', 'dedutivel_irrf', 'tipo'],
                        root: 'result',
                        totalProperty: 'totalRows',
                        baseParams: [{servidor: '', pensao: ''}]
                    });
                }
                return this.store;
            },

            copiar: function(pensao, evento) {
                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('PENSAOGerenciadorPensao', 'copiar'),
                    params: {pensao: pensao, evento: evento},
                    success: function(request) {this.destroy()},
                    failure: function() {alert('Ocorreu um erro tentando copiar eventos.');},
                    scope: this
                });
            }
        }
    );

}