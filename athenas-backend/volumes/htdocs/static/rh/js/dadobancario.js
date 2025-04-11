if(typeof(toolkit.rh.dadobancario) == 'undefined') {
    Ext.ns('toolkit.rh.dadobancario');

    toolkit.rh.dadobancario.Gerenciador = Ext.extend(
        Ext.Window,
        {
            constructor: function(conf) {
                var cf = { title: 'Dado Bancário',width: 750, height: 450, modal: true, closable: true,layout: 'border', conf_obj: conf};
                toolkit.rh.dadobancario.Gerenciador.superclass.constructor.call(this, cf);
                this.setServidor(conf.servidor);
                this.add(this.getDadoBancarioRowGridEditor());
            },

            setServidor: function(servidor){
                this.servidor = servidor;
            },

            getServidor: function(){
                return this.servidor;
            },

            getDadoBancarioDef: function(){
                return Ext.data.Record.create([
                    { name: 'codigo', type: 'string'},
                    { name: 'banco', type: 'string'},
                    { name: 'agencia', type: 'string'},
                    { name: 'conta', type: 'string'},
                    { name: 'tipo_conta', type: 'string'},
                    { name: 'principal', type: 'bool'},
                    { name: 'folha', type: 'string'}
                ]);
            },

            getDadoBancarioObj: function(){
                if(!this.dadoBancarioObj)
                    this.dadoBancarioObj = this.getDadoBancarioDef();
                return this.dadoBancarioObj;
            },

            getWriter: function(){
                if(!this.writer)
                    this.writer = new Ext.data.JsonWriter({encode: true,writeAllFields: false});
                return this.writer;
            },

            getReader: function(){
                if(!this.reader)
                    this.reader = new Ext.data.JsonReader({
                        totalProperty: 'totalRows',
                        successProperty: 'success',
                        root: 'result',
                        start: 0,
                        limit: 5
                    }, this.getDadoBancarioObj());
                return this.reader;
            },

            getProxy: function(){
                if(!this.proxy)
                    this.proxy = new Ext.data.HttpProxy({url: 'RHDadoBancarioGerenciador/get_store/dado_bancario/'});
                return this.proxy;
            },

            getStore: function(){
                if(!this.store)
                    this.store = new Ext.data.Store({
                        id: 'dadobancario',
                        writer: this.getWriter(),
                        reader: this.getReader(),
                        proxy: this.getProxy(),
                        autoLoad: true,
                        autoSave: true,
                        baseParams:{start: 0, limit: 50, servidor: this.getServidor()}
                    });
                return this.store;
            },

            getStoreBanco: function(){
                var obj = toolkit.util.Ajax.request_json(
                    "POST",
                    toolkit.util.Normalize.controller_action(
                        "RHDadoBancarioGerenciador",
                        "get_store/banco"
                    )
                );
                return obj;
            },

            getEditor: function(){
                if(!this.editor)
                    this.editor = new Ext.ux.grid.RowEditor({
                        saveText: 'Salvar',
                        cancelText: 'Cancelar',
                        scope: this,
                        listeners: {
                            scope: this,
                            afteredit: function(object, changes, r, rowIndex) { this.getStore().reload(); },
                            beforeedit: function(rowEditor, rowIndex) {
                                if(this.getStore().getAt(rowIndex).get('codigo')) {
                                    this.getColumn().setEditable(1, false);
                                    this.getColumn().setEditable(2, false);
                                    this.getColumn().setEditable(3, false);
                                    this.getColumn().setEditable(4, false);
                                    this.getColumn().setEditable(5, false);
                                }
                            }
                        }
                    });
                return this.editor;
            },

            getColumn: function(){
                if(!this.column)
                    this.column = new Ext.grid.ColumnModel([
                        {header: 'codigo',dataIndex: 'codigo',width: 50, sortable: true},
                        {
                            header: 'Banco',dataIndex: 'banco',width: 200,sortable: true,
                            editor: {xtype: 'combo',allowBlank: false, store: this.getStoreBanco()}
                        },{
                            header: 'Agencia',dataIndex: 'agencia',width: 100,sortable: true,
                            editor: { xtype: 'textfield',allowBlank: false}
                        },{
                            header: 'Conta',dataIndex: 'conta',width: 100,sortable: true,
                            editor: { xtype: 'textfield',allowBlank: false}
                        },{
                            header: 'Tipo de Conta',dataIndex: 'tipo_conta',width: 80,sortable: true,
                            editor: { xtype: 'combo',allowBlank: false, store: [[1,'CORRENTE'],[2,'POUPANÇA'],[3,'INVESTIMENTO']]}
                        },{
                            header: 'Principal',dataIndex: 'principal',width: 50,sortable: true,
                            editor: { xtype: 'checkbox',allowBlank: false, store: [[1,'CORRENTE'],[2,'POUPANÇA'],[3,'INVESTIMENTO']]}
                        },{
                            header: 'Folha',dataIndex: 'folha',width: 200,sortable: true
                        }
                    ]);
                return this.column;
            },

            getGridPaginator: function() {
                if(!this.gridPaginator) {
                    this.gridPaginator = new Ext.PagingToolbar({
                        autoWidth: true,
                        store: this.getStore(),
                        displayInfo: true,
                        pageSize: 5,
                        prependButtons: true
                    });
                }
                return this.gridPaginator;
            },

            getDadoBancarioRowGridEditor: function(){
                try{
                if(!this.gridEditorDadoBancario){
                    this.gridEditorDadoBancario = new Ext.grid.GridPanel({
                        store: this.getStore(),
                        region:'center',
                        plugins: [this.getEditor()],
                        scope: this,
                        bbar: this.getGridPaginator(),
                        tbar: [{
                            icon: '/' + global.Context + '/static/rh/images/add.png',
                            text: 'Adicionar',
                            scope: this,
                            handler: function(){
                                var db = Ext.data.Record.create([
                                    { name: 'banco', type: 'string'},
                                    { name: 'agencia', type: 'string'},
                                    { name: 'conta', type: 'string'},
                                    { name: 'tipo_conta', type: 'string'},
                                    { name: 'principal', type: 'bool'},
                                    { name: 'folha', type: 'string'}
                                ]);
                                var e = new db({});
                                this.getEditor().stopEditing();
                                this.getStore().insert(0, e);
                                this.getEditor().startEditing(0);
                            }
                        },'-',{
                            ref: '../removeBtn',
                            icon: '/' + global.Context + '/static/rh/images/delete.png',
                            text: 'Remover',
                            scope: this,
                            handler: function(){ this.remove() }
                        },'-',{
                            ref: '../removeBtn',
                            icon: '/' + global.Context + '/static/rh/images/add.png',
                            text: 'Vincular',
                            scope: this,
                            handler: function(){
                                if(this.getDbSelected())
                                    new toolkit.rh.dadobancario.VincularFolha({
                                        servidor: this.getServidor(),
                                        store: this.getStore(),
                                        dado_bancario: this.getDbSelected()
                                    }).show();
                                else alert('Primeiro selecione um Dado bancário!');
                            }
                        }],
                        colModel: this.getColumn(),
                        listeners: {
                            render: function(g) {
                                new Ext.LoadMask(
                                    g.getEl(),
                                    {store: g.getStore(), msg: 'Carregando informações...'}
                                );
                                g.getStore().load({});
                            }
                        }
                    });
                }
                }catch(e){console.debug(e)}
                return this.gridEditorDadoBancario;
            },

            getDbSelected: function(){
                var dbs = [];
                var selection = this.getDadoBancarioRowGridEditor().getSelectionModel().getSelections();
                Ext.each(selection, function(db) { dbs.push(db.get('codigo')) });
                if(dbs.length) return dbs;
                else return undefined;
            },

            remove: function()  {
                var dbs = this.getDbSelected();
                if(dbs) {
                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action(
                            'RHDadoBancarioGerenciador',
                            'remove/dadobancario'
                        ),
                        params: {db: dbs},
                        success: function(request) {
                            var obj = Ext.decode(request.responseText);
                            if(obj.success) this.getStore().reload();
                            else alert('Ocorreram erros tentando remover o Dado Bancário.');
                        },
                        failure: function() {alert('Ocorreram erros tentando remover o Dado Bancário.')},
                        scope: this
                    });
                }else alert('Primeiro selecione um Dado Bancário.');
            }
        });

    toolkit.rh.dadobancario.VincularFolha = Ext.extend(
        Ext.Window,
        {
            
            constructor: function(conf) {
                var cf = {
                    title: 'Adicionar folha ao dado bancário...',
                    closable: true,
                    modal: true,
                    layout: 'border',
                    width: 550,
                    height: 550,
                    conf_obj: conf,
                    buttons:[{text: 'Fechar', scope: this, handler: this.destroy}]
                }
                toolkit.rh.dadobancario.VincularFolha.superclass.constructor.call(this, cf);
                this.add(this.getServidorFolha());
                this.add(this.getFolha());
            },

            getServidorFolha: function(){
                if(!this.gridServidorFolha) {
                    this.gridServidorFolha = new Ext.grid.GridPanel({
                        title: 'Tipos de Folha para o Dado Bancário',
                        region: 'center',
                        sm: new Ext.grid.RowSelectionModel({singleSelect: false}),
                        colModel: new Ext.grid.ColumnModel([
                            {dataIndex: 'descricao', header: 'Descrição', width: 520, sortable: true}
                        ]),
                        tbar:[
                            {
                                ref: '../removeBtn',
                                icon: '/' + global.Context + '/static/rh/images/delete.png',
                                text: 'Remover',
                                scope: this,
                                handler: function(){ this.remove() }
                            }
                        ],
                        bbar: this.getServidorGridPaginator(),
                        store: this.getStoreServidor(),
                        listeners: {
                            render: function(g) {
                                new Ext.LoadMask(
                                    g.getEl(),
                                    {store: g.getStore(), msg: 'Carregando informações...'}
                                );
                                g.getStore().load({});
                            }
                        }
                    });
                }
                return this.gridServidorFolha;
            },

            getStoreServidor: function(){
                if(!this.storeServidor){
                    this.storeServidor = new Ext.data.JsonStore({
                        url: toolkit.util.Normalize.controller_action(
                            'RHDadoBancarioGerenciador',
                            'get_store/servidorfolhatipo'
                        ),
                        fields: ['codigo','descricao'],
                        root: 'result',
                        totalProperty: 'totalRows',
                        baseParams: {dado_bancario: this.conf_obj.dado_bancario},
                        autoLoad: true
                    });
                }
                return this.storeServidor;
            },
            
            getStore: function(){
                if(!this.store){
                    this.store = new Ext.data.JsonStore({
                        url: toolkit.util.Normalize.controller_action(
                            'RHDadoBancarioGerenciador',
                            'get_store/folhatipo'
                        ),
                        fields: ['codigo','descricao'],
                        root: 'result',
                        totalProperty: 'totalRows',
                        autoLoad: true
                    });
                }
                return this.store;
            },

            getFolha: function(){
                if(!this.gridFolha) {
                    this.textSearch = new Ext.form.TextField({
                        emptyText: 'Buscar por matrícula ou nome.',
                        width: 250,
                        enableKeyEvents: true
                    });

                    var label = new Ext.form.Label({
                        text: 'Buscar : ',
                        forId: this.textSearch.getId()
                    });

                    var store = this.getStore();

                    this.textSearch.on(
                        'change',
                        function(obj, newValue) {
                            store.baseParams['start'] = 0;
                            store.baseParams['keyword'] = newValue;
                            store.load({});
                        }
                    );

                    this.textSearch.on(
                        'keypress',
                        function(obj, event) {
                            if(event.getKey() == Ext.EventObject.ENTER) {
                                store.baseParams['start'] = 0;
                                store.baseParams['keyword'] = obj.getValue();
                                store.load({});
                            }
                        }
                    );

                    this.gridFolha = new Ext.grid.GridPanel({
                        title: 'Tipos de Folha',
                        height: 250,
                        region: 'south',
                        sm: new Ext.grid.RowSelectionModel({singleSelect: false}),
                        colModel: new Ext.grid.ColumnModel([
                            {dataIndex: 'descricao', header: 'Descrição', width: 380, sortable: true}
                        ]),
                        bbar: this.getGridPaginator(),
                        store: this.getStore(),
                        tbar:[
                            {
                                icon: '/' + global.Context + '/static/rh/images/add.png',
                                text: 'Adicionar',
                                scope: this,
                                handler: function(){ this.vincular()}
                            },
                            '-',
                            label,
                            ' ',
                            ' ',
                            this.textSearch,
                        ],
                        listeners: {
                            render: function(g) {
                                new Ext.LoadMask(
                                    g.getEl(),
                                    {store: g.getStore(), msg: 'Carregando informações...'}
                                );
                                g.getStore().load({});
                            }
                        }
                    });
                }
                return this.gridFolha;
            },

            getServidorGridPaginator: function() {
                if(!this.gridServidorPaginator) {
                    this.gridServidorPaginator = new Ext.PagingToolbar({
                        autoWidth: true,
                        store: this.getStoreServidor(),
                        displayInfo: true,
                        pageSize: 50,
                        prependButtons: true
                    });
                }
                return this.gridServidorPaginator;
            },

            getGridPaginator: function() {
                if(!this.gridPaginator) {
                    this.gridPaginator = new Ext.PagingToolbar({
                        autoWidth: true,
                        store: this.getStore(),
                        displayInfo: true,
                        pageSize: 50,
                        prependButtons: true
                    });
                }
                return this.gridPaginator;
            },

            getServidorFolhaSelected: function(){
                var folha = [];
                var selection = this.getServidorFolha().getSelectionModel().getSelections();
                Ext.each(selection, function(f) { folha.push(f.get('codigo')) });
                if(folha.length) return folha;
                else return undefined;
            },

            vincular: function() {
                var folha = [];
                Ext.each( this.getFolha().getSelectionModel().getSelections(), function(item) {folha.push(item.get('codigo'));} );
                if(folha.length)
                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action('RHDadoBancarioGerenciador', 'vincular'),
                        params: {dadobancario: this.conf_obj.dado_bancario, folha: folha},
                        success: function(request){
                            this.getStoreServidor().reload()
                            this.conf_obj.store.reload();
                        },
                        failure: function() {alert('Ocorreu um erro tentando vincular folha.');},
                        scope: this
                    });
                else alert('Escolha pelo menos um!');
            },

            remove: function()  {
                var folhas = this.getServidorFolhaSelected();
                if(folhas) {
                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action(
                            'RHDadoBancarioGerenciador',
                            'remove/servidorfolhatipo'
                        ),
                        params: {folha: folhas, dado_bancario: this.conf_obj.dado_bancario},
                        success: function(request) {
                            var obj = Ext.decode(request.responseText);
                            if(obj.success){
                                this.getStoreServidor().reload();
                                this.conf_obj.store.reload();
                            }
                            else alert('Ocorreram erros tentando remover o Tipo de Folha.');
                        },
                        failure: function() {alert('Ocorreram erros tentando remover o Tipo de Folha.')},
                        scope: this
                    });
                }//else alert('Primeiro selecione um Tipo de Folha do Dado Bancário.');
            }
        }
    );

}
