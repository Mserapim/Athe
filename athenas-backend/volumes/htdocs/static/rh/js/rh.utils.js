Ext.ns('toolkit.rh.utils');

Ext.apply(
    toolkit.rh.utils,
    {
        GridNew: Ext.extend(Ext.grid.GridPanel,{
        /*****
         * args deve ser defenido com parametros para formar o gridstore e getcolumnmodel
         *****/
        constructor: function(args) {
            this.args = args;
            this.args.acoes = (undefined == this.args.acoes ? true : this.args.acoes);
            this.args.buttons = args.buttons || {new: true, edit: true, delete: true};

            var cf = {
                height: 150,
                store: this.getGridStore(),
                cm: this.getColumnModel(this.args.controller),
                border: false,
                sm: new Ext.grid.RowSelectionModel({ singleSelect: true }),
                bbar: this.getGridPaginator(),
                autoExpandColumn: 'column_description',
                listeners: {
                    scope: this,
                    dblclick: function() {
                        if(!this.args.acoes){
                            alert('Não é permitido realizar ações através deste compenente!');
                            return;
                        }
                        if(this.args.servidor){
                            new toolkit.widget.ExtCrudForm(
                                {
                                    store: this.getGridStore(),
                                    controller: this.args.controller,
                                    reload_grid: function(){ this.store.reload(); }
                                },
                                toolkit.widget.ExtCrudForm.TYPE.EDIT,
                                this.getSelectionModel().getSelected().get("id"),
                                this.getParamView(this.args.controller)
                            ).show();
                        }else alert("É necessário criar(salvar) um servidor ou selecioná-lo através da pesquisa!");
                    }
                }
            }
            toolkit.rh.utils.GridNew.superclass.constructor.call(this, cf);
            this.on( 'render', function() { this.getGridStore().load({}); }, this);
        },

        getColumnModel: function(controller) {
            if(controller == 'RHDependente' || controller == 'RHServidorVinculo'){
                return new Ext.grid.ColumnModel([
                    {
                        key: 'id',
                        header: 'Chave',
                        width: 50
                    },
                    {
                        id: 'column_description',
                        key: 'description',
                        header: 'Nome',
                        width: 550
                    }
                ]);
            }else if(controller == 'RHServidorLotacao'){
                return new Ext.grid.ColumnModel([
                    {
                        key: 'id',
                        header: 'Chave',
                        width: 50
                    },{
                        id: 'column_description',
                        key: 'description',
                        header: 'Nome',
                        width: 550
                    },{
                        align: 'center',
                        header: 'Ativo',
                        dataIndex: 'status',
                        id: 'status',
                        width: 70,
                        menuDisabled: true,
                        renderer: toolkit.util.formatStatus
                    },{
                        align: 'center',
                        header: 'Arquivo de publicação',
                        dataIndex: 'download',
                        id: 'download',
                        width: 120,
                        menuDisabled: true,
                        renderer: toolkit.util.formatLinks
                    }
                ]);
            }else if(controller == 'RHMovimentacaoPosse'){
                return new Ext.grid.ColumnModel([
                    {
                        key: 'id',
                        header: 'Chave',
                        width: 50
                    },{
                        id: 'column_description',
                        key: 'description',
                        header: 'Nome',
                        width: 550
                    },{
                        key: 'data_exercicio',
                        header: 'Exercício',
                        width: 80
                    },{
                        key: 'data_desligamento',
                        header: 'Desligamento',
                        width: 80
                    },{
                        key: 'tipo_movcarreira',
                        header: 'Provimento',
                        width: 80
                    },{
                        align: 'center',
                        header: 'Ativo',
                        dataIndex: 'status',
                        id: 'status',
                        width: 70,
                        menuDisabled: true,
                        renderer: toolkit.util.formatStatus
                    },{
                        align: 'center',
                        header: 'Arquivo de publicação',
                        dataIndex: 'download',
                        id: 'download',
                        width: 120,
                        menuDisabled: true,
                        renderer: toolkit.util.formatLinks
                    }
                ]);
            }
            else{
                return new Ext.grid.ColumnModel([
                    {
                        key: 'id',
                        header: 'Chave',
                        width: 50
                    },{
                        id: 'column_description',
                        key: 'description',
                        header: 'Nome',
                        width: 550
                    },{
                        align: 'center',
                        header: 'Arquivo de publicação',
                        dataIndex: 'download',
                        id: 'download',
                        width: 120,
                        menuDisabled: true,
                        renderer: toolkit.util.formatLinks
                    }
                ]);
            }
        },

        getGridPaginator: function() {
            if(!this.gridPaginator) {
                this.gridPaginator = new Ext.PagingToolbar({
                    autoWidth: true,
                    store: this.getGridStore(),
                    displayInfo: true,
                    pageSize: 50,
                    prependButtons: true
                })
            }
            return this.gridPaginator;
        },

        getGridStore: function() {
            if(!this.store || (this.args.servidor == undefined)) {
                this.store = new Ext.data.ArrayStore({
                    fields: (this.args.controller == 'RHServidorLotacao') ? ['id', 'description', 'status', 'download'] : ( this.args.controller == 'RHMovimentacaoPosse'? ['id', 'description', 'data_exercicio', 'data_desligamento', 'tipo_movcarreira', 'status', 'download']:['id', 'description', 'download', 'stastus']),
                    url: toolkit.util.Normalize.controller_action(
                        "RHServidorEspecializado",
                        "get_store",
                        [this.args.store_name]
                    ),
                    method: 'POST',
                    baseParams: { servidor: this.args.servidor }
                });
            }
            else if(this.args.servidor == undefined){
                console.debug('servidor indefinido!');
            }
            return this.store;
        },


        getParamView: function(controller){
          if(controller == "RHMovimentacaoDesligamento") return [];
          else if(controller == "GFPMovimentacaoProgressao") return [];
          else if(controller == "RHMovimentacaoReadaptacao") return [];
          else if(controller == "RHMovimentacaoRedistribuicao") return [];
          else return [{ name: "servidor", enabled: false }];
        },

        /**
             * Este método cria a instância do grid e monta o fieldset.
             * @param args[0] = title
             * @param args[1] = field_name
             * @param args[2] = model
             **/
        getFieldSet: function(){
            var father = {
                store: this.getGridStore(),
                controller: this.args.controller,
                reload_grid: function(){ this.store.reload(); }
            };

            return {
                xtype: 'fieldset',
                collapsible: true,
                title: this.args.titulo,
                autoHeight: true,
                autoWidth: true,
                collapsed: true,
                items: [this],
                buttonAlign: 'center',
                scope: this,
                buttons: this.getButtons(father)
            }
        },

        getButtons: function(father)
        {
            var buttons = [];
            if(this.args.acoes)
            {
                if(this.args.buttons.new)
                {
                    buttons.push({
                        text: "Novo",
                        handler: function(){
                            if(this.args.servidor){
                                new toolkit.widget.ExtCrudForm(
                                    father,
                                    toolkit.widget.ExtCrudForm.TYPE.NEW,
                                    false,
                                    [{
                                        name: "servidor",
                                        enabled: false,
                                        value: this.args.servidor
                                    }]
                                ).show();
                            }else alert("É necessário criar(salvar) um servidor ou selecioná-lo através da pesquisa!");
                        },
                        scope: this
                    });
                }

                if(this.args.buttons.edit)
                {
                    buttons.push({
                        text: "Editar",
                        handler: function(){
                            if(!this.args.acoes){
                                alert('Não é permitido realizar ações através deste compenente!');
                                return;
                            }
                            if(this.args.servidor && this.getSelectionModel().getSelected()){
                                new toolkit.widget.ExtCrudForm(
                                    father,
                                    toolkit.widget.ExtCrudForm.TYPE.EDIT,
                                    this.getSelectionModel().getSelected().get("id"),
                                    this.getParamView(this.args.controller)
                                ).show();
                            }else alert("É necessário criar(salvar) um servidor ou selecioná-lo através da pesquisa!");
                        },
                        scope: this
                    });
                }

                if(this.args.buttons.delete)
                {
                    buttons.push({
                        text: "Apagar",
                        handler: function(){
                            if(!this.args.acoes){
                                alert('Não é permitido realizar ações através deste compenente!');
                                return;
                            }
                            if(this.args.servidor){
                                var items = this.getSelectionModel().getSelections();
                                Ext.Msg.show({
                                    title:'Apagar itens selecionados?',
                                    msg: 'Deseja apagar os itens selecionados?',
                                    buttons: Ext.Msg.YESNO,
                                    fn: function(b) {
                                        if(b == "yes"){
                                            Ext.each(
                                                items,
                                                function(record) {
                                                    Ext.Ajax.request({
                                                        url: toolkit.util.Normalize.controller_action(
                                                            this.args.controller,
                                                            "commit",
                                                            ["DELETE", record.get("id"), 0]
                                                        ),
                                                        method: 'POST',
                                                        success: function() {
                                                            this.store.baseParams["servidor"] = this.args.servidor;
                                                            this.store.reload();
                                                        },
                                                        scope: this
                                                    });
                                                },
                                                this
                                            );
                                        }
                                    },
                                    icon: Ext.MessageBox.QUESTION,
                                    scope: this
                                });
                            }else alert("É necessário criar(salvar) um servidor ou selecioná-lo através da pesquisa!");
                        },
                        scope: this
                    });
                }
            }
            return buttons;
        }
    }),

    CustomGridPanel: Ext.extend(toolkit.plugins.JsonGridPanel,{
        constructor: function(cf) {
            this.cf = cf;
            this.cf.title = this.cf.title ? this.cf.title : 'Não declarado';
            this.cf.pageSize = this.cf.pageSize ? this.cf.pageSize : 50;
            this.cf.readerFields = (this.cf.readerFields == undefined ? [{name: '_pk'},{name: '_nome'},] : this.cf.readerFields);
            this.cf.store = this.cf.store ? this.cf.store : this.getStore();
            this.cf.colModel = this.cf.colModel ? this.cf.colModel : this.getColumnModel();
            this.cf.bbar = this.cf.bbar ? this.cf.bbar : this.buildBottomToolbar();
            this.cf.sm = this.cf.sm ? this.cf.sm : this.getselModelGridPanel();
            this.cf.method_list = cf.method_list != undefined ? cf.method_list : 'list';
            toolkit.rh.utils.CustomGridPanel.superclass.constructor.call(this, this.cf);
        },

        getProxy: function(){
            this.cf.method_list = this.cf.method_list != undefined ? this.cf.method_list : 'list';
            if(!this.proxyGridPanel){
                this.proxyGridPanel = new Ext.data.HttpProxy({
                    scope: this,
                    method: 'POST',
                    api: {
                        read : toolkit.util.Normalize.controller_action(this.cf.controller, this.cf.method_list),
                        create : toolkit.util.Normalize.controller_action(this.cf.controller, 'create'),
                        update: toolkit.util.Normalize.controller_action(this.cf.controller, 'update'),
                        destroy: toolkit.util.Normalize.controller_action(this.cf.controller, 'delete')
                    }
                });
            }
            return this.proxyGridPanel;
        },

        getReader: function(){
            if(!this.readerGridPanel){
                this.readerGridPanel = new Ext.data.JsonReader({
                        totalProperty: 'totalRows',
                        successProperty: 'success',
                        idProperty: (this.cf.readerFields[0].name == '_pk' ? '_pk' : 'pk'),
                        root: 'result',
                        messageProperty: 'message'  // <-- New "messageProperty" meta-data
                    },
                    this.cf.readerFields
                );
            }
            return this.readerGridPanel;
        },

        getWriter: function(){
            if(!this.writerGridPanel){
                this.writerGridPanel = new Ext.data.JsonWriter({
                    encode: true,
                    writeAllFields: false
                });
            }
            return this.writerGridPanel;
        },

        getStore: function(){
            if(!this.storeGridPanel){
                    this.storeGridPanel = new Ext.data.Store({
                        id: 'store',
                        autoLoad: false,
                        proxy: this.getProxy(),
                        reader: this.getReader(),
                        writer: this.getWriter(),  // <-- plug a DataWriter into the store just as you would a Reader
                        autoSave: true // <-- false would delay executing create, update, delete requests until specifically told to do so with some [save] buton.
                    });
                if(this.cf.readerFields[0].name == '_pk')
                    this.storeGridPanel.loadData({"totalRows": 11, "result": [{'_pk':'1', '_nome':'Fulano'},{'_pk':'2', '_nome':'Cicrano'}]});
            }
            return this.storeGridPanel;
        },

        getselModelGridPanel: function(){
            if(!this.selModelGridPanel){
                this.selModelGridPanel = new Ext.grid.RowSelectionModel({singleSelect:true});
            }
            return this.selModelGridPanel;
        },

        getColumnModel: function(){
            if(!this.colModelGridPanel){
                if(this.cf.readerFields[0].name == '_pk'){
                    this.colModelGridPanel = new Ext.grid.ColumnModel({
                        columns: [
                            this.getselModelGridPanel(),
                            {header: "Código", sortable: false, dataIndex: "_pk", key: "_pk", id: "_pk", width: 50},
                            {header: "Nome", sortable: false, dataIndex: "_nome", key: "_nome", id: "_nome", width: 400}
                        ]
                    });
                }else{
                    this.colModelGridPanel = new Ext.grid.ColumnModel({
                        columns: [
                            this.getselModelGridPanel(),
                            {header: "Código", sortable: false, dataIndex: "pk", key: "pk", id: "pk", width: 50},
                            {header: "Nome", sortable: false, dataIndex: "nome", key: "nome", id: "nome", width: 400}
                        ]
                    });
                }
            }
            return this.colModelGridPanel;
        },

        buildBottomToolbar: function() {
            return new Ext.PagingToolbar({
                store: this.getStore(),
                pageSize: this.cf.pageSize,
                displayInfo: true
            });
        }
    }),

    CustomFieldSet: Ext.extend(Ext.form.FieldSet,{
        constructor: function(cf) {
            this.cf = cf;
            toolkit.rh.utils.CustomFieldSet.superclass.constructor.call(this, this.cf);
        }
    }),

    ExtCrudCall: function(args) {
        this.store = (args.store ? args.store : undefined);
        this.controller = (args.controller ? args.controller : undefined);
        if(args.tipo == undefined || args.tipo == 'NEW')
            this.tipo = toolkit.widget.ExtCrudForm.TYPE.NEW;
        else if(args.tipo == 'EDIT')
            this.tipo = toolkit.widget.ExtCrudForm.TYPE.EDIT;
        else if(args.tipo == 'DELETE')
            this.tipo = 3;

        this.pk = (args.pk ? args.pk : undefined);
        this.fields = (args.fields ? args.fields : {});

        this.call = function(){
            new toolkit.widget.ExtCrudForm(
                {
                    store: this.store,
                    controller: this.controller,
                    reload_grid: function(){ this.store.reload(); }
                },
                this.tipo,
                (this.pk == undefined ? false : this.pk),
                this.fields
            ).show();
        };
    }

});