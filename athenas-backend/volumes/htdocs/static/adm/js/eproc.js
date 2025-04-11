
if(typeof(toolkit.adm.eproc) == 'undefined') {

    Ext.ns('toolkit.adm.eproc');

    /**
     * Registra na pilha de Tipos de Processo, para serem criados no gestor de processo.
     * 
     * @param conf Configuração dos tipos de processos, com as seguintes informações:
     * {
     *      title: 'Titulo',
     *      object: Definição do objeto
     * }
     */
    toolkit.adm.eproc.registraTipoProcesso = function(conf) {
        var flag = false;

        Ext.each(
            toolkit.adm.eproc.TipoProcesso,
            function(registro) {
                if(registro.titulo == conf.titulo || registro.object == conf.object) {
                    flag = true
                    return false;
                }

                return true;
            }
        );

        if(!toolkit.adm.eproc.tipoProcesso) toolkit.adm.eproc.tipoProcesso = [];
        if(!flag) toolkit.adm.eproc.tipoProcesso.push(conf);
    };

    toolkit.adm.eproc.Processo = Ext.extend(
        Ext.Window,
        {
            controller: 'EPProcesso',
            
            getFirstTab: function() {
                if(!this.firstTab) {
                    this.firstTab = new Ext.Panel({
                        layout: 'form',
                        autoRender: true,
                        title: 'Informações',
                        frame: true,
                        labelWidth: 140,
                        defaults: {
                            width: 385
                        },
                        items: [
                            {
                                xtype: 'numberfield',
                                fieldLabel: 'Numero do Processo',
                                name: 'numero',
                                emptyText: 'Somente o número do processo sem as formatações.',
                                value: this.conf.values.numero ? this.conf.values.numero : '',
                                readOnly: this.conf.values.numero != undefined,
                                disabled: this.conf.values.numero != undefined
                            },
                            {
                                xtype: 'datefield',
                                fieldLabel: 'Data do Processo',
                                name: 'data',
                                value: this.conf.values.data ? this.conf.values.data : '',
                                readOnly: this.conf.values.data != undefined,
                                disabled: this.conf.values.data != undefined
                            },
                            {
                                xtype: 'textfield',
                                fieldLabel: 'Título',
                                name: 'titulo',
                                value: this.conf.values.titulo ? this.conf.values.titulo : '',
                                readOnly: this.conf.values.titulo != undefined,
                                disabled: this.conf.values.titulo != undefined
                            },
                            {
                                xtype: 'autocomplete',
                                fieldLabel: 'Interessado',
                                name: 'interessado',
                                displayField: 'description',
                                valueField: 'pk',
                                store: new Ext.data.JsonStore({
                                    url: toolkit.util.Normalize.controller_action(
                                        this.controller,
                                        'autocomplete'
                                    ),
                                    baseParams: {
                                        model: 'Servidor'
                                    },
                                    root: 'result',
                                    fields: ['pk', 'description']
                                }),
                                conf: {
                                    canAdd: false,
                                    canEdit: false
                                },
                                controller: 'RHServidor',
                                value: this.conf.values.interessado ? this.conf.values.interessado : '',
                                readOnly: this.conf.values.interessado != undefined,
                                disabled: this.conf.values.interessado != undefined
                            },
                            {
                                xtype: 'xhtmleditor',
                                fieldLabel: 'Descrição',
                                name: 'descricao',
                                value: this.conf.values.descricao ? this.conf.values.descricao : ''
                            }
                        ]
                    });
                }

                return this.firstTab
            },
            
            getTabPanel: function() {
                if(!this.tabPanel) {
                    this.tabPanel = new Ext.TabPanel({
                        activeTab: 0,
                        region: 'center',
                        border: false,
                        items: [
                            this.getFirstTab()
                        ]
                    });
                }

                return this.tabPanel
            },
            
            getFormPanel: function() {
                if(!this.formPanel) {
                    this.formPanel = new Ext.form.FormPanel({
                        layout: 'border',
                        region: 'center',
                        border: false,
                        width: 545,
                        height: 330,
                        items: this.getTabPanel()
                    });
                }

                return this.formPanel;
            },

            commit: function() {
                var form = this.getFormPanel().getForm();

                form.waitMsgTarget = this.getEl();

                form.submit({
                    url: toolkit.util.Normalize.controller_action(
                        this.controller,
                        (this.conf.values.pk ? 'update' : 'create')
                    ),
                    params: {
                        processo: this.conf.values ? this.conf.values.pk : undefined
                    },
                    validate: 'client',
                    waitMsg: 'Gravando dados do processo...',
                    success: function(form, action) {
                        if(this.conf.scope) {
                            this.conf.scope.__call__ = this.conf.trigger;
                            this.conf.scope.__call__();
                            this.conf.scope.__call__ = undefined;
                        }
                        
                        this.destroy();
                    },
                    failure: function(form, action) {
                        console.debug(action);
                    },
                    scope: this
                });
            },
            
            constructor: function(conf) {

                if(conf && !conf.values) conf.values = {};
                else if(!conf) conf = {values: {}}

                var cf = {
                    title: 'Processo',
                    closable: true,
                    modal: true,
                    width: 560,
//                    height: 400,
                    height: 420,
                    layout: 'border',
                    border: false,
                    buttons: [
                        {
                            text: 'Salvar',
                            handler: this.commit,
                            scope: this
                        },
                        {
                            text: 'Fechar',
                            handler: this.destroy,
                            scope: this
                        }
                    ],
                    conf: conf
                };

                toolkit.adm.eproc.Processo.superclass.constructor.call(this, cf);

                this.add(this.getFormPanel());
            }
        }
    );

    toolkit.adm.eproc.registraTipoProcesso({
        icon: 'static/adm/images/processo.png',
        title: 'Processo',
        object: toolkit.adm.eproc.Processo
    });

    toolkit.adm.eproc.Gerenciador = Ext.extend(
        Ext.grid.GridPanel,
        {
            controller: 'EPGerenciador',

            refresh: function() {
                this._getStore().reload();
            },

            create: function(object) {
                new object({
                    trigger: this.refresh,
                    scope: this
                }).show();
            },

            edit: function() {
                var selected = this.getSelectionModel().getSelected();

                if(selected) {
                    var object = eval(selected.get('controller'));

                    new object({
                        values: selected.json.values,
                        trigger: this.refresh,
                        scope: this
                    }).show();
                }
                else alert('Primeiro selecione um item antes de pedir a edição.');
            },

            del: function() {
                var selected = this.getSelectionModel().getSelections();
                var processos = [];

                if(selected) {
                    Ext.each(
                        selected,
                        function(item) {
                            processos.push(item.get('values').pk);
                        }
                    );

                    Ext.Msg.show({
                        title: 'Removendo Processos',
                        msg: 'Tem certeza que deseja remover os processos selecionados?',
                        icon: Ext.Msg.QUESTION,
                        buttons: Ext.Msg.YESNO,
                        scope: this,
                        fn: function(action) {
                            if(action == 'yes')
                                Ext.Ajax.request({
                                    url: toolkit.util.Normalize.controller_action(
                                        'EPGerenciador',
                                        'remove'
                                    ),
                                    params: { processos: processos },
                                    success: this.refresh,
                                    failure: this.refresh,
                                    scope: this
                                });

                        }
                    });
                }
                else alert('Primeiro selecione um item antes de pedir a remoção.');
            },
            
            _getToolbar: function() {
                if(!this.toolBar) {

                    var novo = {
                        text: 'Novo',
                        iconCls: true,
                        icon: '/' + global.Context + '/static/images/document-sing.png',
                        menu: []
                    }

                    Ext.each(
                        toolkit.adm.eproc.tipoProcesso,
                        function(conf) {
                            novo.menu.push({
                                text: conf.title,
                                handler: function() {this.create(conf.object);},
                                scope: this,
                                icon: conf.icon ? conf.icon : false,
                                iconCls: conf.icon != undefined
                            });
                        },
                        this
                    );

                    this.toolBar = new Ext.Toolbar({
                        items: [
                            novo,
                            {
                                text: 'Editar',
                                iconCls: true,
                                icon: '/' + global.Context + '/static/images/document-open.png',
                                scope: this,
                                handler: this.edit
                            },
                            {
                                text: 'Remover',
                                iconCls: true,
                                icon: '/' + global.Context + '/static/images/delete.png',
                                scope: this,
                                handler: this.del
                            },
                            '-',
                            {
                                xtype: 'label',
                                text: 'Buscar por : ',
                                forId: this.getSearchField().getId()
                            },
                            ' ',
                            ' ',
                            {
                                xtype: 'panel',
                                border: false,
                                items: [
                                    this.getSearchField()
                                ]
                            },
                            ' ',
                            ' ',
                            {
                                iconCls: true,
                                icon: '/' + global.Context + '/static/images/clean.png'
                            },
                            '-'
                        ]
                    });
                }

                return this.toolBar;
            },

            getSearchField: function() {
                if(!this.searchField) {
                    this.searchField = new Ext.form.TextField({
                        emptyText: 'Texto para ser utilizado como criterio de busca.',
                        width: 325
                    });
                }

                return this.searchField
            },
            
            _getBottombar: function() {
                if(!this.bottomBar) {
                    this.bottomBar = new Ext.PagingToolbar({
                        store: this._getStore(),
                        displayInfo: true
                    });
                }

                return this.bottomBar;
            },

            _getStore: function() {
                if(!this._store) {
                    this._store = new Ext.data.JsonStore({
                        url: toolkit.util.Normalize.controller_action(
                            this.controller,
                            'list'
                        ),
                        method: 'POST',
                        baseParams: {},
                        root: 'result',
                        fields: ['status', 'numero', 'titulo', 'interessado', 'controller', 'values'],
                        totalProperty: 'totalRows',
                        autoLoad: true
                    });
                }

                return this._store
            },

            constructor: function() {
                var cf = {
                    title: 'Gerenciador de Processos',
                    closable: true,
                    store: this._getStore(),
                    cm: new Ext.grid.ColumnModel([
                        {
                            header: '',
                            dataIndex: 'status',
                            id: 'status',
                            menuDisabled: true,
                            width: 45,
                            renderer: toolkit.util.formatStatus
                        },
                        {
                            header: 'Numero',
                            dataIndex: 'numero',
                            sortable: true,
                            width: 105
                        },
                        {
                            header: 'Título',
                            dataIndex: 'titulo',
                            sortable: true,
                            width: 345
                        },
                        {
                            header: 'Interessado',
                            dataIndex: 'interessado',
                            sortable: true,
                            width: 345
                        }
                    ]),
                    tbar: this._getToolbar(),
                    bbar: this._getBottombar(),
                    listeners: {
                        scope: this,
                        dblclick: this.edit
                    }
                };

                toolkit.adm.eproc.Gerenciador.superclass.constructor.call(this, cf);

                var ts = toolkit.Application.tabspace;
                ts.remove(toolkit.Application.tabspace.getActiveTab());
                ts.add(this);
            }
        }
    );

}