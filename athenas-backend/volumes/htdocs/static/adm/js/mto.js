if(typeof(toolkit.adm.mto) == 'undefined') {
    Ext.ns('toolkit.adm.mto');
    toolkit.adm.mto.Gerenciador = Ext.extend(
        Ext.Panel,
        {

            _not_implemented: function(){
                console.debug("not implemented");
            },

            constructor: function(args) {
                var cf = {
                    title: 'Elemento de Despesa',
                    closable: true,
                    layout: {
                        type:'vbox',
                        padding:'5',
                        align:'stretch'
                    },
                    defaults:{margins:'0 0 5 0'}

                };

                toolkit.adm.mto.Gerenciador.superclass.constructor.call(this, cf);

                var active = toolkit.Application.tabspace.getActiveTab();
                toolkit.Application.tabspace.remove(active);
                toolkit.Application.tabspace.add(this);

                this.add(this.getPanelElementoDespesa());
                this.add(this.getPanelSubitem());

                var obj = this;
                setTimeout(function() {
                    obj.doLayout();
                }, 50);

                this.on(
                    'render',
                    function() {
                        this.getStoreGridElementoDespesa().load({
                            params:{
                                start: 0,
                                limit: 50
                            }
                        });
                    },
                    this
                );
            },

            /*****
             *
             *    PANEL ELEMENTO DESPESA
             *
             **/
            getPanelElementoDespesa: function(){
                if(!this.panelElementoDespesa){
                    this.panelElementoDespesa = new Ext.grid.GridPanel({
                        title: "<b>Elemento Despesa</b>",
                        cm: this.getElementoDespesaColumnModel(),
                        store: this.getStoreGridElementoDespesa(), //store do grid???
                        border: true,
                        flex: 1,
                        sm: new Ext.grid.RowSelectionModel({
                            singleSelect:false,
                             listeners: {
                                 scope: this,
                                 rowselect: function(sm) {
                                    this.getStoreGridSubitem().baseParams['elemento_despesa'] = sm.getSelected().get('codigo');
                                    this.getStoreGridSubitem().load({params:{start:0, limit:50}});
                                 }
                             }
                        }),
                        bbar: this.getElementoDespesaGridPaginator(),
                        tbar: this.getElementoDespesaGridToolbar(),
                         listeners: {
                             scope: this,
                             dblclick: function() {
                                if(this.panelElementoDespesa.getSelectionModel().getSelected()){
                                    new toolkit.widget.ExtCrudForm(
                                        this.getFatherElementoDespesa('elemento_despesa'),
                                        toolkit.widget.ExtCrudForm.TYPE.EDIT,
                                        this.panelElementoDespesa.getSelectionModel().getSelected().get('codigo')
                                    ).show();
                                }
                             }
                         }
                    });
                }
                return this.panelElementoDespesa;
            },

            getFatherElementoDespesa: function(tipo) {
                var father = false;

                var dict = {
                    elemento_despesa: 'MTOElementoDespesa'
                }

                father = {
                    store: this.getStoreGridElementoDespesa(),
                    controller: dict[tipo],
                    reload_grid: function(){
                        this.store.reload();
                    }
                };

                return father;
            },

            getStoreGridElementoDespesa: function() {
                if(!this.storeGridElementoDespesa) {
                    this.storeGridElementoDespesa = new Ext.data.JsonStore({
                        fields: [
                            "codigo",
                            "numero",
                            "descricao"
                        ],
                        root: "result",
                        totalProperty: "totalRows",
                        url: toolkit.util.Normalize.controller_action(
                            "MTOElementoDespesaCuston",
                            "get_store",
                            ["elemento_despesa"]
                        ),
                        remoteSort: true
                    });
                }
                return this.storeGridElementoDespesa;
            },

            getElementoDespesaColumnModel: function() {
                if(!this.elementoDespesaColumnModel) {
                    this.elementoDespesaColumnModel = new Ext.grid.ColumnModel([
                        {dataIndex: 'codigo', header: 'Código', sortable: true, width: 50},
                        {dataIndex: 'numero', header: 'Número', sortable: true, width: 100},
                        {dataIndex: 'descricao', header: 'Descrição', sortable: true, width: 300},
                    ]);
                }
                return this.elementoDespesaColumnModel;
            },

            getElementoDespesaGridPaginator: function() {
                if(!this.gridPaginator) {
                    this.gridPaginator = new Ext.PagingToolbar({
                        autoWidth: true,
                        store: this.getStoreGridElementoDespesa(),
                        displayInfo: true,
                        pageSize: 50,
                        prependButtons: true
                    })
                }
                return this.gridPaginator;
            },

            addElementoDespesa: function(type) {
                new toolkit.widget.ExtCrudForm(
                    this.getFatherElementoDespesa(type),
                    toolkit.widget.ExtCrudForm.TYPE.NEW,
                    false,
                    []
                ).show();
            },

            editElementoDespesa: function() {
                if(this.panelElementoDespesa.getSelectionModel().getSelected()){
                    new toolkit.widget.ExtCrudForm(
                        this.getFatherElementoDespesa('elemento_despesa'),
                        toolkit.widget.ExtCrudForm.TYPE.EDIT,
                        this.panelElementoDespesa.getSelectionModel().getSelected().get('codigo')
                    ).show();
                }
                else alert('Primeiro selecione uma capacitação para edição.')
            },

            deleteElementoDespesa: function(record) {
                var controller = this.getFatherElementoDespesa('elemento_despesa').controller;

                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action(
                        controller,
                        "commit",
                        ["DELETE", record.get("codigo"), 0]
                    ),
                    method: 'POST',
                    success: function() {
                        this.getStoreGridElementoDespesa().reload();
                    },
                    scope: this
                });
            },

            deleteElementosDespesa: function() {
                if(this.panelElementoDespesa.getSelectionModel().getSelections()){
                    var items = this.panelElementoDespesa.getSelectionModel().getSelections();
                    Ext.Msg.show({
                        title:'Apagar itens selecionados?',
                        msg: 'Deseja apagar os itens selecionados?',
                        buttons: Ext.Msg.YESNO,
                        fn: function(b) {if(b == "yes") Ext.each(items, this.deleteElementoDespesa, this);},
                        icon: Ext.MessageBox.QUESTION,
                        scope: this
                    });
                }
                else alert("É necessário selecionar o(s) item(ns)!");
            },

            getElementoDespesaGridToolbar: function() {
                var menu = [];
                menu.push({
                    text: "Novo",
                    iconCls: true,
                    icon: "/" + global.Context + "/static/images/add.png",
                    scope: this,
                    handler: function(){ this.addElementoDespesa('elemento_despesa');}
                });
                menu.push({
                    text: "Editar",
                    iconCls: true,
                    icon: "/" + global.Context + "/static/images/edit.png",
                    handler: this.editElementoDespesa,
                    scope: this
                });
                menu.push({
                    text: "Excluir",
                    iconCls: true,
                    icon: "/" + global.Context + "/static/images/delete.png",
                    handler: this.deleteElementosDespesa,
                    scope: this
                });
                menu.push("-");
                return menu;
            },

            /*****
             *
             *    PANEL ELEMENTO DESPESA SUBITEM
             *
             **/
            getPanelSubitem: function(){
                if(!this.panelSubitem){
//                    var father_subitem = {
//                        store: this.getStoreGridSubitem(),
//                        controller: "GCAPInscricao",
//                        reload_grid: function(){
//                            this.store.reload();
//                        }
//                    };
                    this.panelSubitem = new Ext.grid.GridPanel({
                        title: "<b>SubItems de Elemento de Despesa</b>",
                        store: this.getStoreGridSubitem(),
                        cm: this.getSubitemColumnModel(),
                        border: true,
                        flex: 1,
                        sm: new Ext.grid.RowSelectionModel({singleSelect:false}),
                        bbar: this.getSubitemGridPaginator(),
                        tbar: this.getSubitemGridToolbar(),
                        listeners: {
                            scope: this,
                            dblclick: this.editSubitem
                        }
                    });
                }
                return this.panelSubitem;
            },

            getStoreGridSubitem: function() {
                if(!this.storeGridSubitem) {
                    this.storeGridSubitem = new Ext.data.JsonStore({
                        fields: [
                            "codigo",
                            "numero",
                            "descricao",
                            "elemento_despesa"
                        ],
                        root: "result",
                        totalProperty: "totalRows",
                        url: toolkit.util.Normalize.controller_action(
                            "MTOElementoDespesaCuston",
                            "get_store",
                            ["elemento_despesa_subitem"]
                        ),
                        baseParams:{
                            elemento_despesa: "",
                            start:0,
                            limit:50
                        },
                        remoteSort: true
                    });
                }
                return this.storeGridSubitem;
            },

            getSubitemColumnModel: function() {
                if(!this.subitemColumnModel) {
                    this.subitemColumnModel = new Ext.grid.ColumnModel([
                        {dataIndex: 'codigo', header: 'Código', sortable: true, width: 50},
                        {dataIndex: 'numero', header: 'Número', sortable: true, width: 100},
                        {dataIndex: 'descricao', header: 'Descrição', sortable: true, width: 100}
                    ]);
                }
                return this.subitemColumnModel;
            },

            getSubitemGridPaginator: function() {
                if(!this.subitemGridPaginator) {
                    this.subitemGridPaginator = new Ext.PagingToolbar({
                        autoWidth: true,
                        store: this.getStoreGridSubitem(),
                        displayInfo: true,
                        pageSize: 50,
                        prependButtons: true
                    })
                }
                return this.subitemGridPaginator;
            },

            getFatherSubitem: function() {
                return {
                    store: this.getStoreGridSubitem(),
                    controller: "MTOElementoDespesaSubItem",
                    reload_grid: function(){
                        this.store.reload();
                    }
                };
            },

            addSubitem: function() {
                if(this.panelElementoDespesa.getSelectionModel().getSelected()) {
                    new toolkit.widget.ExtCrudForm(
                        this.getFatherSubitem(),
                        toolkit.widget.ExtCrudForm.TYPE.NEW,
                        false,
                        [{
                            name: "elemento_despesa",
                            enabled: false,
                            value: this.panelElementoDespesa.getSelectionModel().getSelected().get('codigo')
                        }]
                    ).show();
                }
                else alert("Escolha um Elemento de Despesa!")
            },

            editSubitem: function() {
                var selected = this.panelElementoDespesa.getSelectionModel().getSelected();
                var iSelected = this.getPanelSubitem().getSelectionModel().getSelected();

                if(selected && iSelected) {
                    new toolkit.widget.ExtCrudForm(
                        this.getFatherSubitem(),
                        toolkit.widget.ExtCrudForm.TYPE.EDIT,
                        this.panelSubitem.getSelectionModel().getSelected().get('codigo'),
                        [{
                            name: "elemento_despesa",
                            enabled: false,
                            value: this.panelElementoDespesa.getSelectionModel().getSelected().get('codigo')
                        }]
                    ).show();
                }
                else alert("Escolha um Elemento de Despesa!")
            },

            deleteSubitem: function() {
                var selection = this.panelSubitem.getSelectionModel();

                if(selection.getSelections()) {
                    Ext.Msg.show({
                        title: 'Excluir as Subitems',
                        msg: 'Tem certeza que deseja excluir os subitems selecionados?',
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
                                        subitem: ic
                                    },
                                    success: function(request) {
                                        var result = Ext.decode(request.responseText);
                                        this.getStoreGridSubitem().reload();
                                    },
                                    failure: function() {
                                        alert('Ocorreu um erro tentando excluir os subitems selecionados.');
                                    },
                                    scope: this
                                })
                            }
                        },
                        icon: Ext.Msg.QUESTION,
                        scope: this
                    })
                }
                else alert('Primeiro você deve selecionar os subitems que deseja excluir.')
            },

            getSubitemGridToolbar: function() {
                if(!this.SubitemToolbar) {
                    this.SubitemToolbar = new Ext.Toolbar({
                        items: [
                            {
                                text: "Novo",
                                iconCls: true,
                                icon: "/" + global.Context + "/static/images/add.png",
                                scope: this,
                                handler: this.addSubitem
                            },
                            {
                                text: "Editar",
                                iconCls: true,
                                icon: "/" + global.Context + "/static/images/edit.png",
                                scope: this,
                                handler: this.editSubitem
                            },
                            {
                                text: "Excluir",
                                iconCls: true,
                                icon: "/" + global.Context + "/static/images/delete.png",
                                scope: this,
                                handler: this.deleteSubitem
                            },
                            '-',
                        ]
                    });
                }

                return this.SubitemToolbar;
            }

        }
    );
}
