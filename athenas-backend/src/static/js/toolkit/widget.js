/**
 *
 */

if(typeof(toolkit) == "undefiend" || typeof(toolkit.util) == "undefined") {
    alert("BUG: O 'toolkit.util' não está presente.");
}

/**
 * Biblioteca de Widgets
 */
toolkit.widget = {
    /**
     * Utilizado para contar o numero de unique id que já foram gerados.
     */
    _count: 0,

    /**
     * Retorna um UNIQUE ID para ser utilizado na DOM.
     */
    get_next_id: function() {
        return "unique_id_" + (toolkit.widget._count++);
    }
}

toolkit.widget.TabPanel = Ext.extend(Ext.Panel, {
    constructor: function(cfg) {
        Ext.apply(cfg, {
            closable: true
        });

        toolkit.widget.TabPanel.superclass.constructor.call(this, cfg);

        var active = toolkit.Application.tabspace.getActiveTab();

        if (active && active.id !== 'cmp-dashboard-app') {
            toolkit.Application.tabspace.remove(active);
        }

        toolkit.Application.tabspace.add(this);
        toolkit.Application.tabspace.setActiveTab(this);
    }
});

toolkit.widget.Frame = Ext.extend(Ext.Viewport, {
    constructor: function()
    {
        var cf = {
            layout:'border',
            items: [
                {
                    region:'north',
                    html: new Ext.Template(
                        '<div id="header">',
                            '<h1>Portal do Servidor</h1>',
                        '</div>'
                    ).apply()
                },
                {region:'center'},
                {
                    region: 'south',
                    height: 30,
                    html: new Ext.Template(
                        '<div class="warnings">',
                            '<p>Seja bem vindo(a) ao Novo Sistema de Gestão de Pessoas e Vida Funcional do MPMT. Em caso de dúvidas entre em contato com o suporte através do telefone (65) 3613-5166 ou pelo e-mail suporte@mpmt.mp.br</p>',
                        '</div>'
                    ).apply()
                }
            ]
        }

        toolkit.widget.Frame.superclass.constructor.call(this, cf);
    }
});


/*
Widget de recuperação de senha
*/
toolkit.widget.PasswordRecover = Ext.extend(Ext.Window, {

    constructor: function()
    {
        toolkit.widget.PasswordRecover.superclass.constructor.call(this, {
            title: 'Recuperação de Senha',
            modal: true,
            frame: true,
            layout: 'fit',
            autoHeight: true,
            autoWidth: true,
            items: [this._getCheckForm()]
        });
    },

    _getCheckForm: function()
    {
        if(!this._checkForm)
        {
            this._checkForm = Ext._create('Ext.form.FormPanel', {
                height: 75,
                padding: 5,
                border: false,
                items: [
                    {
                        xtype: 'textfield',
                        fieldLabel: 'Nome de usuário',
                        name: 'username',
                        width: 250
                    }
                ],
                buttons:[
                    {
                        text: 'Recuperar',
                        scope: this,
                        handler: function()
                        {
                            var _this = this,
                                checkForm = this._getCheckForm().getForm(),
                                username = checkForm.getValues().username;


                            this._submitForm({
                                form: checkForm,
                                url: 'AuthBase/recover',
                                success: function(form, action)
                                {
                                    r = action.result;
                                    if(r.success)
                                    {
                                        Ext.Msg.alert('Alerta', r.msg);

                                        _this.removeAll();
                                        _this.add(_this._getResetForm(username));
                                        _this.doLayout();
                                        _this.center();
                                    }
                                }
                            });
                        }
                    }
                ]
            });
        }

        return this._checkForm;
    },

    _getResetForm: function(username)
    {
        if(!this._resetForm)
        {
            this._resetForm = Ext._create('Ext.form.FormPanel', {
                height: 130,
                padding: 5,
                border: false,
                labelWidth: 125,
                labelAlign: 'right',
                items: [
                    {
                        xtype: 'hidden',
                        name: 'username',
                        width: 250
                    },
                    {
                        xtype: 'textfield',
                        fieldLabel: 'Código de verificação',
                        name: 'key',
                        width: 250
                    },
                    {
                        xtype: 'textfield',
                        fieldLabel: 'Nova senha',
                        name: 'new_password',
                        inputType: 'password',
                        width: 250
                    },
                    {
                        xtype: 'textfield',
                        fieldLabel: 'Confirmação de senha',
                        name: 'password_confirmation',
                        inputType: 'password',
                        width: 250
                    }

                ],
                buttons: [
                    {
                        text: 'Salvar',
                        scope: this,
                        handler: function()
                        {
                            var resetForm = this._getResetForm(username).getForm()
                                scope = this;

                            resetForm.setValues({username: username});

                            this._submitForm({
                                form: resetForm,
                                url: 'AuthBase/reset',
                                success: function(form, action)
                                {
                                    r = action.result;

                                    if(r.success)
                                    {
                                        toolkit.util.messageDialog('Alerta', r.msg);
                                        scope.close();
                                        scope.destroy();
                                    }
                                }
                            });
                        }
                    }
                ]
            });
        }

        return this._resetForm;
    },

    _validateSubmitParams: function(params)
    {
        if(!params.form)
            throw Exception('É necessário informar a instância do formulário que deseja submeter.');
        if(!params.url)
            throw Exception('É necessário informar a url para onde quer submeter o formulário.');
    },

    _submitForm: function(params)
    {
        var overrides = params || {},
            defaults = {
                waitMsg: 'Aguarde...',
                form: null,
                url: null,
                success: null,
                failure: null
            },
            config = Ext.apply(defaults, overrides);

        this._validateSubmitParams(config)

        params.form.submit({
            scope: this,
            // clientValidation: true,
            url: toolkit.util.action(config.url),
            method: 'POST',
            success: function(form, action)
            {
                if(config.success)
                    config.success(form, action);
            },
            failure: function(form, action)
            {
                if(config.failure)
                    config.failure(form, action)
                else
                {
                    var msg = action.result.msg || 'Verifique o preenchimento do formulário.';
                    toolkit.util.errorDialog(msg, action.result.errors, params.form);
                }
            },
            waitMsg: config.waitMsg
        });
    }
});


/**
 * Widget de Login
 */
toolkit.widget.ExtLogin = Ext.extend(
    Ext.Window,
    {
        getFormPanel: function() {
            if(!this.formPanel) {
                this.formPanel = new Ext.form.FormPanel({
                    style: 'margin: 5px 5px 5px 5px',
                    border: false,
                    width: 390,
                    labelWidth: 120,
                    labelAlign: 'right',
                    defaults: {
                        width: 260
                    },
                    items: [
                        {
                            xtype: 'textfield',
                            name: 'login',
                            fieldLabel: 'Nome de Usuário',
                            allowBlank: false,
                            listeners: {
                                scope: this,
                                render: function(field) {
                                    setTimeout(function() {field.focus()}, 500);
                                }
                            }
                        },
                        {
                            xtype: 'textfield',
                            name: 'passwd',
                            inputType: 'password',
                            fieldLabel: 'Senha de acesso',
                            allowBlank: false,
                            enableKeyEvents: true,
                            listeners: {
                                scope: this,
                                keypress: function(text, event) {
                                    if (event.getCharCode() == event.RETURN) {
                                        this.connect();
                                    }
                                }
                            }
                        },
                        {
                            xtype: 'combo',
                            hiddenName: 'theme',
                            fieldLabel: 'Ambiente',
                            store: [
                                [1, 'Cinza'],
                                [0, 'Azul'],
                                [2, 'Acessível para deficientes visuais'],
                            ],
                            triggerAction: 'all',
                            value: DEFAULT_THEME,
                            allowBlank: false,
                            editable: false
                        }
                    ],
                    'buttonAlign': 'left',
                    buttons: [
                        // {
                        //     'text': 'Recuperação de Senha',
                        //     'handler': function() {
                        //         Ext._create('toolkit.widget.PasswordRecover').show();

                        //         // new Ext.Window({
                        //         //     'title': 'Alteração de Senha',
                        //         //     'modal': true,
                        //         //     'layout': 'fit',
                        //         //     'height': 450,
                        //         //     'width': 600,
                        //         //     'html': '<iframe style="border:none;width:100%;height:100%" src="http://mpto.mp.br/pwd/"></iframe>'
                        //         // }).show();
                        //     }
                        // },
                        '->',
                        {
                            text: 'Cancelar',
                            scope: this,
                            handler: this.cancel,
                            iconCls: true,
                            icon: '/' + global.Context + '/static/images/delete.png'
                        },
                        {
                            text: 'Autenticar',
                            scope: this,
                            handler: this.connect,
                            iconCls: true,
                            icon: '/' + global.Context + '/static/images/login.png'
                        }
                    ]
                });
            }

            return this.formPanel;
        },

        connect: function() {
            var form = this.getFormPanel().getForm();

            form.waitMsgTarget = this.getFormPanel().ownerCt.getEl();

            form.submit({
                clientValidation: true,
                url: toolkit.util.Normalize.controller_action(
                    'ExtLogin',
                    'connect'
                ),
                method: 'POST',
                success: function(form, action) {
                    location.reload();
                },
                failure: function(form, action) {
                    if(action.failureType == 'client') {
                        alert('Verifique o preenchimento do formulário.')
                    }
                    else {
                            var pss = form.findField('passwd');

                            pss.setValue('');
                            pss.focus();
                            pss.markInvalid(action.result.msg);

                            alert(action.result.msg);
                        }
                },
                waitMsg: 'Autenticando...'
            })
        },

        cancel: function() {
            location.href = 'http://athenas.mp.to.gov.br/athenas';
        },

        constructor: function() {
            var cf = {
                title: 'Serviço de Identificação do Usuário',
                closable: false,
                draggable: false,
                //modal: true,
                resizable: false,
                iconCls: 'icon_login',
                items: [
                    {
                        xtype: 'panel',
                        border: false,
                        items: [this.getFormPanel()]
                    }
                ],
                listeners:{
                    show: function() { new toolkit.widget.Frame().show(); }
                }
            }

            toolkit.widget.ExtLogin.superclass.constructor.call(this, cf);
        }
    }
);


/**
 * Widget de FirstAccess
 */
toolkit.widget.ExtFirstAccess = Ext.extend(
    Ext.Window,
    {
        getFormPanel: function() {
            if(!this.formPanel) {
                this.formPanel = new Ext.form.FormPanel({
                    style: 'margin: 5px 5px 5px 5px',
                    border: false,
                    width: 400,
                    labelWidth: 120,
                    labelAlign: 'left',
                    items: [
                        {
                            width: 270,
                            xtype: 'textfield',
                            name: 'cpf',
                            fieldLabel: 'CPF',
                            allowBlank: false
                        },
                        {
                            width: 270,
                            xtype: 'textfield',
                            name: 'matricula',
                            fieldLabel: 'Matrícula',
                            allowBlank: false
                        },
                        {
                            width: 270,
                            xtype: 'datefield',
                            name: 'nascimento',
                            fieldLabel: 'Nascimento',
                            allowBlank: false
                        }
                    ],
                    buttons: [
                        {
                            text: 'Validar',
                            scope: this,
                            handler: this.connect,
                            iconCls: true,
                            icon: '/' + global.Context + '/static/images/login.png'
                        },
                        {
                            text: 'Cancelar',
                            scope: this,
                            handler: this.cancel,
                            iconCls: true,
                            icon: '/' + global.Context + '/static/images/delete.png'
                        }
                    ]
                });
            }

            return this.formPanel;
        },

        getPanelLocalizacao: function(){
            if(this.panelLocalizacao == undefined){
                this.panelLocalizacao = new Ext.form.FieldSet({
                    title: 'Lotação',
                    layout: 'fit',
                    collapsible: false,
                    width: 400,
                    height: 240,
                    items: [
                        this.setComboInicial(1),
                    ],
                    scope: this,
                    listeners:{
                        scope: this,
                        afterrender: function(component){
                            this.appendCombo(component.get(1), this.contador, component.get(1).getValue(), component.get(1).store.data.items[0].data['field3']);
                        }
                    }
                });
            }
            return this.panelLocalizacao;
        },

        getPanelDuvida: function(){
            if(this.panelDuvida == undefined){
                this.panelDuvida = new Ext.form.FieldSet({
                    title: '',
                    layout: 'fit',
                    html: '<div style="padding:1px 1px 1px 1px">Primeira etapa do processo de marcação de Férias 2011/2012.<br> Confirme seus dados e indique sua lotação.<br> Para maiores esclarecimentos clique <a href="http://www.mp.to.gov.br/web/portal/manuais/2011/09/12/recursos-humanos-inicia-processo-de-marcacao-de-ferias-20112012-dos-servidores-do-mpe" TARGET="_blank">aqui</a>. </div>',
                    collapsible: false,
                    width: 400,
                    height: 75,
                    items: [],
                    scope: this
                });
            }
            return this.panelDuvida;
        },

        setComboInicial: function(contador){
            var combo = this.getCombo({conteiner: this, pai: "", contador: contador, editable: false});
            combo.setValue(combo.store.data.items[0].data['field1']);
            return combo;
        },

        setSegundoComboInicial: function(contador){
            var combo = this.getCombo({conteiner: this, pai: this.getPanelLocalizacao().get(1).getValue(), contador: contador, editable: true});
            return combo;
        },

        getCombo: function(conf){
            this.contador = conf.contador + 1;
            var combo = new toolkit.widget.comboBoxGeneric({conteiner: conf.conteiner, pai: conf.pai, contador: conf.contador, editable: conf.editable});
            return combo;
        },

        appendCombo: function(combo, combo_id, pai, filho){
            var atual = combo_id + 1;
            while(combo_id <= this.contador){
                combo_id = combo_id + 1;
                this.removeCombo(combo_id);
            }
            this.contador = atual;
            if(filho > 0){
                this.panelLocalizacao.add(this.getCombo({conteiner: this, pai: pai, contador: this.contador, editable: true}));
                this.panelLocalizacao.doLayout();
            }
        },

        removeCombo: function(combo){
            this.panelLocalizacao.remove(combo);
            this.panelLocalizacao.doLayout();
        },

        getComboValue: function(){
            var i = this.contador;
            var valor = undefined;
            while(i != 0){
                try{
                    valor = this.getPanelLocalizacao().get(i).getValue();
                }catch(e){;}
                if(valor != undefined && valor != '')
                    break;
                i--;
            }
            return valor;
        },

        connect: function() {
            var form = this.getFormPanel().getForm();
            form.waitMsgTarget = this.getFormPanel().ownerCt.getEl();

            console.debug('--> debug <--');

            form.submit({
                clientValidation: true,
                url: toolkit.util.Normalize.controller_action(
                    'ExtLogin',
                    'first_access'
                ),
                method: 'POST',
                success: function(form, action) {
                    setTimeout('location.reload()', 2000);
                },
                failure: function(form, action) {
                    if(action.failureType == 'client') {
                        alert('Verifique o preenchimento do formulário.')
                    }
                    else {
                        var pss = form.findField('cpf');
                        pss.focus();
                        alert(action.result.msg);
                    }
                },
                waitMsg: 'Validando primeiro acesso...'
            })
        },

        cancel: function() {
            location.href = 'http://athenas.mp.to.gov.br/athenas';
        },

        constructor: function() {
            var cf = {
                title: 'Primeiro Acesso ao Sistema Athenas',
                closable: false,
                draggable: false,
                modal: true,
                resizable: false,
                iconCls: 'icon_login',
                width: 425,
                items: [
                    {
                        xtype: 'panel',
                        border: false,
                        items: [this.getFormPanel()]
                    }
                ],
                listeners:{
                    render: function(){ setTimeout('location.reload()',240000);}
//                    render: function(){ setTimeout('location.reload()',120000);}
                }
            };
            this.lotacoes = [];
            this.localizacao = undefined;

            toolkit.widget.ExtFirstAccess.superclass.constructor.call(this, cf);
        }
    }
);

toolkit.widget.comboBoxGeneric = Ext.extend(
    Ext.form.ComboBox,
    {

        constructor: function(conf) {
            var cf = {
                id: conf.contador,
                editable: conf.editable,
                conteiner: conf.conteiner,
                store: this.getStore(conf.pai),
                allowBlank: true,
                selectOnFocus: true,
                hiddenName: conf.contador,
                width: 377,
                xtype: "combo",
                style: "margin-bottom: 5px",
                blankText: "É necessário preencher este campo.",
                displayField: "description",
                mode: "local",
                triggerAction: "all",
                listeners:{
                    scope: this,
                    select: function(combo, record, index) {
                        this.conteiner.appendCombo(combo, combo.id, record.get('field1'), record.get('field3'));
                    }
                }
            };

            toolkit.widget.comboBoxGeneric.superclass.constructor.call(this, cf);
        },

        getStore: function(pai){
            var obj = toolkit.util.Ajax.request_json(
                "POST",
                toolkit.util.Normalize.controller_action(
                    "RHServidorLocalizacao",
                    "store",
                    [pai]
                )
            );
            return obj;
        }
    }
);

toolkit.widget.ControllerPanel = Ext.extend(
    Ext.Panel,
    {
        constructor: function(cf) {

            var cfg = {
                title: cf.title,
                closable: true,
                layout: 'fit',
                items: [
                    new Ext.Panel({
                        border: true,
                        items: [
                            new Ext.Panel({
                                style: 'margin: 5px 5px 5px 5px',
                                border: true,
                                layout: 'fit'
                            })
                        ]
                    })
                ],
                listeners: {
                    render: function(panel) {
                        setTimeout(function() {toolkit.Application.tabspace.ownerCt.doLayout();}, 1);
                    }
                }
            }

            toolkit.widget.ControllerPanel.superclass.constructor.call(this, cfg);

            var active = toolkit.Application.tabspace.getActiveTab();
            toolkit.Application.tabspace.remove(active);
            toolkit.Application.tabspace.add(this);
        }
    }
);

/**
 * Construtor de uma instancia de toolkit.widget.ExtCrud.
 * @param controller: Controller utilizado para manipular o CURD.
 * @return Retorna a instancia de um toolkit.widget.ExtCrud
 */
toolkit.widget.ExtCrud = function(controller, searchable) {
    this.parent = toolkit.Application.tabspace;
    this.controller = controller;
    this.searchable = searchable;

    this.id = "form_crud_" + toolkit.widget.get_next_id();
}

toolkit.widget.ExtCrud.prototype = {

    id: null,

    controller: null,

    parent: null,

    filter: null,

    page: {
        num_row: 10,
        active: 0,
        last: 0
    },

    grid_date: null,

    /**
     * Mostra o Widget de um CRUD.
     */
    show: function() {
        this.action_list();
    },

    /**
     * Atualiza a tabview do Viewport.
     */
    refresh: function() {
        this.parent.add(this.panel);
        this.parent.remove(this.parent.getActiveTab());
        this.parent.setActiveTab(this.panel);
        this.panel.doLayout();
    },

    /**
     * Metodo utilizado para criar os botões do Crud.
     * @return Retorna um Array de botões.
     */
    get_actions: function() {
        //TODO: Copiar actions daqui.
        return [
        {
            text: "Novo",
            handler: function() {
                this.action_new();
            },
            scope: this
        },{
            text: "Editar",
            handler: function() {
                this.action_edit();
            },
            scope: this
        },{
            text: "Deletar",
            handler: function() {
                this.action_delete();
            },
            scope: this
        }
        ];
    },

    /**
     * Prepara para criação da grid que será utilizada como visualização dos dados do CRUD.
     */
    action_list: function() {
        var result = toolkit.util.Ajax.request_json(
            "POST",
            toolkit.util.Normalize.controller_action(this.controller, "get_title", ["PANEL"])
        );

        var ft = toolkit.util.Ajax.request_json(
            "POST",
            toolkit.util.Normalize.controller_action(this.controller, "get_title", ["LIST"])
        );

        this.panel = new Ext.Panel({
            title: result.title,
            tooltip: result.title,
            closable: true,
            border: false,
            buttonAlign: "center",
            buttons : this.get_actions(),
            items: [
                {
                    border: false,
                    xtype: "panel",
                    html: "<h1 style=\"text-align:center\">" + ft.title + "</h1>",
                    style: "margin: 10pt"
                },
                this._create_grid()
            ]
        });

        this.panel.on(
            "afterlayout",
            function() {
                this.panel.setHeight(this.panel.ownerCt.getBox().height - 60);
                this.grid.setHeight(this.panel.ownerCt.getBox().height - 160);
            },
            this
        )

        this.refresh();
    },

    /**
     * Recarrega a grid na visualização do CRUD.
     */
    reload_grid: function() {
        if(this.store)
            this.store.load({
                param: {}
            });
        else
            alert("Bug: ExtCrud: O reload só pode ser evocado quando o grid estiver criado.");
    },

     _create_grid: function() {
         this.store = new Ext.data.JsonStore({
            url: toolkit.util.Normalize.controller_action(
                this.controller,
                "query"
            ),
            root: "result",
            totalProperty: "totalRows",
            fields: toolkit.util.Ajax.request_json(
                "POST",
                toolkit.util.Normalize.controller_action(
                    this.controller,
                    "get_field_list"
                )
            ),
            remoteSort: true
         });

         try {
             var cols = toolkit.util.Ajax.request_json(
                "POST",
                toolkit.util.Normalize.controller_action(
                    this.controller,
                    "get_columns_grid"
                )
             );

             var toSearch = [];

             Ext.each(
                cols,
                function(item) {
                    if(item.renderer){
                        var func= false;
                        try{
                            func= eval(item.renderer);
                        }
                        catch(e){}
                        item.renderer= func;

                    }
                    if(item.toSearch) {
                        toSearch.push(item)
                    }
                }
             );

             this.grid = new toolkit.plugins.JsonGridPanel({
                store: this.store,
                style: "margin: 10pt",
                height: 300,
                searchable: this.searchable,
                controller: this.controller,
                sm: new Ext.grid.RowSelectionModel({
                     singleSelect: true
                }),
                cm: new Ext.grid.ColumnModel(cols),
                toSearch: toSearch,
                listeners: {
                    scope: this,
                    dblclick: function() {
                        this._action_edit();
                    },
                    keypress: function(event) {
                        switch(event.getKey()) {
                            case event.DELETE:
                                this.action_delete();
                                event.stopEvent();
                                break;
                            case event.ENTER:
                                this.action_edit();
                                event.stopEvent();
                                break;
                            case event.INSERT: case event.N:
                                this.action_new();
                                event.stopEvent();
                                break;
                            case event.UP: case event.DOWN: case event.LEFT: case event.RIGHT:
                                break;
                        }
                    }
                }
             });
         }
         catch(e) {
             console.debug(e);
         }

         return this.grid;
     },

    /**
     * Cria um formulário para criação de um novo elemento no CRUD.
     */
    action_new: function() {
        var frm = new toolkit.widget.ExtCrudForm(this,toolkit.widget.ExtCrudForm.TYPE.NEW);

        frm.show();
    },

    /**
     * Cria um formulário para edição de um item selecionado na GRID.
     */
    action_edit: function() {
        var data = this.grid.getSelectionModel().getSelected();

        if(data) {
            var frm = new toolkit.widget.ExtCrudForm(this, 2, data.get("id"));
            frm.show();
        }
        else {
            alert("Primeiro você deve selecionar um item na lista.");
        }
    },

     /**
     * Cria um formulário para edição de um item selecionado na GRID.
     */
    _action_edit: function() {
        this.action_edit();
    },
    /**
     * Cria um formulário para deleção de um item selecionado na GRID.
     */
    action_delete: function() {
        var data = this.grid.getSelectionModel().getSelected();

        if(data) {
            var id = data.get("id");
            var fn = function(bnt, text, opts) {

                if(bnt == "yes") {
                    var obj = toolkit.util.Ajax.request_json(
                        "POST",
                        toolkit.util.Normalize.controller_action(this.controller, "commit", ["DELETE", id, 0])
                    );

                    this.reload_grid();
                }
                else if(bnt == "no") {
                    var frm = new toolkit.widget.ExtCrudForm(this, 3, id);
                    frm.show();
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
                msg : "Tem certeza que deseja remover o item com id " + id + ", caso não tenha certeza clique em <b>Não</b> para visualizar os dados.",
                fn : fn,
                scope: this,
                buttons: Ext.MessageBox.YESNOCANCEL,
                icon: Ext.MessageBox.QUESTION
            });
        }
        else {
            alert("Primeiro você deve selecionar um item na lista.");
        }
    }
}

/**
 * Exception para NULLPOINTER.
 */
toolkit.widget.ExtNullPointerException = function(message) {
    this.message = (message != null ? message : "Ocorreu uma exceção de objeto Nulo.");
}

toolkit.widget.ExtNullPointerException.prototype = {
    /**
     * Mensagem da Exceção
     */
    message: null,

    /**
     * Transforma a exceção em uma String para ser usado junto com window.alert.
     */
    toString: function() {
        return this.message;
    }
}

/**
 * Instancia um novo toolkit.widget.ExtCrudForm.
 * @param father, Crud pai do Form, father deve ter o atributo controller.
 * @param type, Tipo do formulário, veja toolkit.widget.ExtCrudForm.TYPE.
 * @param id, Id da entidade a ser manipulada pelo Form.
 * @return Retorna uma instancia de toolkit.widget.ExtCrudForm.
 */
toolkit.widget.ExtCrudForm = function(father, type, id, initial) {

    if(father != null)
        this.father = father;
    else
        throw new toolkit.widget.ExtNullPointerException("Bug: O objeto pai é requirido.");

    this.type = type;

    if(type != this.TYPE.NEW) {
        if(id != null)
            this.eid = id;
        else
            throw new toolkit.widget.ExtNullPointerException("Bug: É necessário repassar o id ao objeto.");
    }

    this.initial = initial != undefined ? initial : {};

    this.objects = {};
}

/**
 * Tipo de formulários
 */
toolkit.widget.ExtCrudForm.TYPE = {
    NEW: 1,
    EDIT: 2,
    DELETE: 3,
    VIEW: 4
}

toolkit.widget.ExtCrudForm.prototype = {

    TYPE : toolkit.widget.ExtCrudForm.TYPE,

    father: null,

    type: null,

    eid: 0,

    objects : {},

    /**
     * Metodo utilizado para realizar o commit dos dados.
     * @param type, Tipo do commit.
     * @param and_close, Caso este setado como Falso o form não será fechado apresentando um novo form limpo.
     */
    action_commit: function(type, and_close) {
        var close;

        if(and_close == null)
            close = true;
        else
            close = and_close;

        var result;
        var data = this.objects.form.getForm().getValues();

        var url;

        if(type == "NEW")
            url = toolkit.util.Normalize.controller_action(this.father.controller, "validate");
        else
            url = toolkit.util.Normalize.controller_action(this.father.controller, "validate", [type, this.eid]);

        obj = toolkit.util.Ajax.request_json(
            "POST",
            url,
            data
            );

        if(obj.result) {

            if(type == 1)
                obj = toolkit.util.Ajax.request_json(
                    "POST",
                    toolkit.util.Normalize.controller_action(this.father.controller, "commit", [type,]),
                    data
                );
            else
                obj = toolkit.util.Ajax.request_json(
                    "POST",
                    toolkit.util.Normalize.controller_action(this.father.controller, "commit", [type, this.eid]),
                    data
                );

            if(obj.result) {
                try{
                    this.father.reload_grid(toolkit.plugins.element_add, obj.last_id, obj.value);
                }catch(e){
                    this.father.reload_grid();
                }
                if(close) this.objects.wnd.close();
                else {
                    this.objects.form.getForm().reset();
                    this.objects.form.getForm().items.get(0).focus();
                }
            }
        } else {
            var flag = false;
            var form = this.objects.form.getForm();
            var error, component;

            for(var idx in obj.errors) {
                if(!isNaN(idx)) {
                    error = obj.errors[idx];
                    if(error.field != "__all__") {
                        component = form.findField(error.field);
                        component.markInvalid(error.description);
                    }
                    else {
                        flag = true;
                        alert(error.description);
                    }
                }
            }
            if(!flag)
                alert("O formulário não foi preenchido corretamente. Verifique o preenchimento e tente novamente.");

            this.objects.wnd.doLayout();
        }

        return obj;
    },

    /**
     * Metodo utilziado para criar o Ext.form.Panel.
     * @param html, HTML a ser utilizado para dar conteudo ao Ext.form.Panel.
     * @return Retorna a instancia de um Ext.form.Panel
     */
    _create_form_panel: function(fields) {
        var bnts = [];
        var type;

        if(this.type == this.TYPE.NEW) {
            type = "NEW";

            bnts = [
            {
                text: "Salva",
                handler: function() {
                    this.action_commit(type);
                },
                scope: this
            },{
                text: "Salva e Novo",
                handler: function() {
                    this.action_commit(type, false);
                },
                scope: this
            },

            ];
        }
        else if(this.type == this.TYPE.EDIT) {
            type = "EDIT";

            bnts = [
            {
                text: "Salva",
                handler: function() {
                    this.action_commit(type);
                },
                scope: this
            },

            ];
        }
        else if(this.type == this.TYPE.DELETE){
            type = "DELETE";

            bnts = [
            {
                text: "Salva",
                handler: function() {
                    this.action_commit(type);
                },
                scope: this
            },

            ];
        }
        else if(this.type == this.TYPE.VIEW){
            type = "DELETE";

            bnts = [
            {
                text: "Anterior",
                handler: this.action_prev,
                scope: this
            },{
                text: "Próximo",
                handler: this.action_next,
                scope: this
            },
            ];
        }
        else {
            type = "NOT_DEFINED_IN_LIST_TYPE";
        }

        bnts.push({
            text: "Fechar",
            handler: function() {
                this.objects.wnd.close();
            },
            scope: this
        });

        var panel = new Ext.FormPanel({
            border: false,
            autoHeight: true,
            buttons : bnts,
            buttonAlign: "right",
            width: 510,
            items: fields
        });

        panel.on(
            "afterlayout",
            function(panel) {
                if(this.getComponent(0).baseCls == "x-tab-panel") {
                    var cmp = this.getComponent(0);

                    for(var idx = cmp.items.getCount(); idx >= 0; idx--) {
                        var itm = cmp.getComponent(idx);
                        cmp.setActiveTab(itm);
                    }
                }

                if(!panel.flag) {
                    var values = panel.getForm().getValues();

                    if(panel.flag == undefined)
                        panel.flag = 1;

                    for(var fieldName in values) {
                        if(panel.flag >= 2) {
                            panel.flag++;
                            panel.getForm().findField(fieldName).focus();
                            console.debug(panel.flag);
                            break;
                        }
                    }
                }
            },
            panel
        );

        return panel;
    },

    action_next: function() {
        switch(this.type) {
            case 1:
                type = "NEW";
                break;
            case 2:
                type = "EDIT";
                break;
            case 3:
                type = "DELETE";
                break;
            case 4:
                type = "VIEW";
                break;
        }

        this.eid++;

        if(this.type != 1)
            this.objects.form = this._create_form_panel(
                toolkit.util.Ajax.request_text("POST", toolkit.util.Normalize.controller_action(this.father.controller, "action_form", [type, this.eid]))
                );
        else
            this.objects.form = this._create_form_panel(
                toolkit.util.Ajax.request_text("POST", toolkit.util.Normalize.controller_action(this.father.controller, "action_form", [type,]))
                );

        this.objects.wnd.removeAll();
        this.objects.wnd.add(this.objects.form);
        this.objects.wnd.render();
    },

    action_prev: function() {
        switch(this.type) {
            case 1:
                type = "NEW";
                break;
            case 2:
                type = "EDIT";
                break;
            case 3:
                type = "DELETE";
                break;
            case 4:
                type = "VIEW";
                break;
        }

        this.eid--;

        if(this.eid == 0) this.eid = 1;

        if(this.type != 1)
            this.objects.form = this._create_form_panel(
                toolkit.util.Ajax.request_text("POST", toolkit.util.Normalize.controller_action(this.father.controller, "action_form", [type, this.eid]))
                );
        else
            this.objects.form = this._create_form_panel(
                toolkit.util.Ajax.request_text("POST", toolkit.util.Normalize.controller_action(this.father.controller, "action_form", [type,]))
                );

        this.objects.wnd.removeAll();
        this.objects.wnd.add(this.objects.form);
        this.objects.wnd.render();
    },

    /**
     * Mostra o Form.
     */
    show: function() {

        var type;
        var bnts;

        switch(this.type) {
            case 1:
                type = "NEW";
                break;
            case 2:
                type = "EDIT";
                break;
            case 3:
                type = "DELETE";
                break;
            case 4:
                type = "VIEW";
                break;
        }
        var xml;

        if(this.type != 1){
            this.objects.form = this._create_form_panel(
                toolkit.util.Ajax.request_json(
                    "POST",
                    toolkit.util.Normalize.controller_action(
                        this.father.controller,
                        "action_form",
                        [type, this.eid]
                        )
                    )
                );
        }
        else{
            this.objects.form = this._create_form_panel(
                toolkit.util.Ajax.request_json(
                    "POST",
                    toolkit.util.Normalize.controller_action(
                        this.father.controller,
                        "action_form",
                        [type,]
                        )
                    )
                );
        }


        this.objects.wnd = new Ext.Window({
            title: toolkit.util.Ajax.request_json("POST",toolkit.util.Normalize.controller_action(this.father.controller, "get_title", [type,])).title,
            items: [this.objects.form],
            layout: "fit",
            autoHeight: true,
            closable: true,
            modal: true,
            scripts: true,
            shadow: false
        });

        this.objects.form.on(
            "afterlayout",
            function() {
                Ext.each(
                    this.initial,
                    function(fieldInfo) {
                        try {
                            var field = this.objects.form.getForm().findField(fieldInfo.name);
                            if(fieldInfo.baseParams != undefined && field['store']){
                                st= field.getStore();
                                Ext.apply(st.baseParams, fieldInfo.baseParams);
                            }
                            if(fieldInfo.value) field.setValue(fieldInfo.value);
                            if(fieldInfo.enabled != undefined && !fieldInfo.enabled) {
                                field.setReadOnly(!fieldInfo.enabled);
                                field.addClass('x-item-disabled');
                            }
                        }
                        catch(e) {}
                    },
                    this
                );
            },
            this
        )

        this.objects.wnd.show();

    }
}

/**
 * Implementa CRUD somente visualização.
 */
toolkit.widget.ExtCrudView = function(controller) {
    toolkit.widget.ExtCrud.apply(this, [controller]);
}

toolkit.widget.ExtCrudView.prototype.get_actions = function() {
    return [
    {
        text: "Visualizar",
        handler: function() {
            var frm = new toolkit.widget.ExtCrudForm(this, 4, this.grid_data.id);
            frm.show();
        },
        scope: this
    }
    ];
}

/**
 * toolkit.widget.ExtCrudView herda toolkit.widget.ExtCrud
 */
toolkit.widget.ExtCrudView = toolkit.util.PrototypeManipulator.extend(
    toolkit.widget.ExtCrudView,
    toolkit.widget.ExtCrud
    );

/**
 * Implementa CRUD com botões configuraveis.
 */
toolkit.widget.ExtConfigurableButtonsCrud = function(controller, searchable) {
    toolkit.widget.ExtCrud.apply(this, [controller]);

    url = toolkit.util.Normalize.controller_action(this.controller, "buttons", []);
    obj = toolkit.util.Ajax.request_json("POST", url);

    this.insertable = obj["insert"];
    this.editable   = obj["edit"];
    this.deletable  = obj["delete"];
    this.view       = obj["view"];
    this.searchable = searchable;
}

toolkit.widget.ExtConfigurableButtonsCrud.prototype = {

    get_actions: function() {
        var bnts = [];

        if(this.insertable)
            bnts.push({
                text: "Novo",
                handler: function() {
                    this.action_new();
                },
                scope: this
            });
        else if(this.editable)
            bnts.push({
                text: "Editar",
                handler: function() {
                    this.action_edit();
                },
                scope: this
            });
        else if(this.deletable)
            bnts.push({
                text: "Deletar",
                handler: function() {
                    this.action_delete();
                },
                scope: this
            });
        else if(this.view)
            bnts.push({
                text: "Visualizar",
                handler: function() {
                    var data = this.grid.getSelectionModel().getSelected();
                    var frm = new toolkit.widget.ExtCrudForm(this, 4, data.get("id"));
                    frm.show();
                },
                scope: this
            });

        return bnts;
    }
}

/**
 * toolkit.widget.ExtConfigurableButtonsCrud herda toolkit.widget.ExtCrud
 */
toolkit.widget.ExtConfigurableButtonsCrud = toolkit.util.PrototypeManipulator.extend(
    toolkit.widget.ExtConfigurableButtonsCrud,
    toolkit.widget.ExtCrud
);

toolkit.widget.ExtConfigurableButtonsCrud.prototype._action_edit = function() {
    var data = this.grid.getSelectionModel().getSelected();

    if(data) {
        var frm = new toolkit.widget.ExtCrudForm(this, 4, data.get("id"));
        frm.show();
    }
    else {
        alert("Primeiro você deve selecionar um item na lista.");
    }
}

toolkit.widget.ExtReportBuild = function(controller, report) {
    this.controller = controller;
    this.report     = report;
}

toolkit.widget.ExtReportBuild.Status = {
    SUCCESS            :     0,
    JASPER_NOT_FOUND   :     1,
    NOT_FOUND_DB       :     2,
    UKNOW_ERROR        :     3,
    DB_NOT_CONECTED    :     4,
    SRC_NOT_CONECTED   :     5,
    OPENED             :     6,
    WAITING            :     7,
    UKNOW              :     8,
    NOT_FOUND          :     9,
    SESSION_EXPIRED    :    10,
    SESSION_NOT_FOUND  :    11,
    STARTED            :    12,
    JAR_NOT_FOUND      :   256,
    COMMAND_NOT_FOUND  : 32512
}

toolkit.widget.ExtReportBuild.prototype = {

    startDownload: function(form) {
        var values;

        if(form instanceof Ext.form.BasicForm) {
            if(!form.isValid()) {
                alert('O formulário não foi preenchido corretamente, verifique e tente novamente.')
                return;
            }
            else values = form.getValues();
        }
        else values = form;

        var url = toolkit.util.Normalize.controller_action(
            this.controller,
            "download",
            [this.session.sid]
        ) + "?" + toolkit.util.QueryBuild.build(values);

        var width  = 235;
        var height = 175;
        var left   = (screen.width - width) / 2;
        var top    = (screen.height - height) / 2;

        window.open(url, "_self");

        try {form.reset();} catch(e) { }
    },

    runReport: function(type, form) {
        var values;

        if(form instanceof Ext.form.BasicForm) {
            if(!form.isValid()) {
                alert('O formulário não foi preenchido corretamente, verifique e tente novamente.')
                return;
            }
            else values = form.getValues();
        }
        else values = form;


        this.session = toolkit.util.Ajax.request_json(
            'GET',
            toolkit.util.Normalize.controller_action(
                this.controller,
                "create_session"
            )
        )

        this.monitor = new toolkit.thread.Simple({
            period: 2000,
            handler: function() {
                var obj = toolkit.util.Ajax.request_json(
                    'POST',
                    toolkit.util.Normalize.controller_action(
                        this.controller,
                        "get_status_session"
                    ),
                    {
                        sid: this.session.sid
                    }
                );

                switch(obj.status) {
                    case toolkit.widget.ExtReportBuild.Status.STARTED:
                    case toolkit.widget.ExtReportBuild.Status.OPENED:
                        break;
                    case toolkit.widget.ExtReportBuild.Status.SUCCESS:
                        this.startDownload(form);
                        this.dei();
                        break;
                    case toolkit.widget.ExtReportBuild.Status.NOT_FOUND_DB:
                    case toolkit.widget.ExtReportBuild.Status.JASPER_NOT_FOUND:
                    case toolkit.widget.ExtReportBuild.Status.DB_NOT_CONECTED:
                    case toolkit.widget.ExtReportBuild.Status.UKNOW_ERROR:
                    case toolkit.widget.ExtReportBuild.Status.SRC_NOT_CONECTED:
                    case toolkit.widget.ExtReportBuild.Status.JAR_NOT_FOUND:
                    case toolkit.widget.ExtReportBuild.Status.COMMAND_NOT_FOUND:
                        alert(
                            "Não foi possível encontrar algumas informações para gerar o relatório.\n" +
                            "Entre em contato com o Administrador e relate o erro.\n" +
                            "Código do erro foi " + obj.status + ".\n" +
                            "Telefone: (63) 3216-7564"
                        );
                        this.dei();
                        break;
                    case toolkit.widget.ExtReportBuild.Status.SESSION_EXPIRED:
                        alert(
                            "Sua solicitação expirou, favor tentar novamente mais tarde.\n" +
                            "Se o problema persistir entre em contato com Administrador.\n" +
                            "Telefone: (63)3216.7564"
                        );
                        this.dei();
                        break;
                    default:
                        alert("Condição desconhecida ERROR(" + obj.status + ")");
                        this.dei();
                }
            }
        });

        this.monitor.session       = this.session;
        this.monitor.startDownload = this.startDownload;
        this.monitor.controller    = this.controller;
        this.monitor.form          = form;
        this.monitor.start();

        toolkit.util.Ajax.request_json(
            'POST',
            toolkit.util.Normalize.controller_action(
                this.controller,
                "run_report",
                [this.session.sid]
            ),
            values
        );
    },

    show: function() {

        this.form = new Ext.FormPanel({
            border: false,
            items: [
                toolkit.util.Ajax.request_json(
                    "GET",
                    toolkit.util.Normalize.controller_action(
                        this.controller,
                        "action_form"
                    )
                )
            ]
        });

        this.panel = new Ext.Panel({
            title: toolkit.util.Ajax.request_json(
                "GET",
                toolkit.util.Normalize.controller_action(
                    this.controller,
                    "get_title",
                    ["TITLE"]
                )
            ).title,
            closable: true,
            autoScroll: true,
            items: [
                {
                    xtype: "panel",
                    bodyBorder: false,
                    width: 515,
                    style: "margin: 0 auto; padding-top: 4em",
                    title: toolkit.util.Ajax.request_json(
                                "GET",
                                toolkit.util.Normalize.controller_action(
                                    this.controller,
                                    "get_title",
                                    ["SUB_TITLE"]
                                )
                            ).title,
                    items: [
                        this.form
                    ],
                    buttonAlign: "center",
                    buttons: [
                        {
                            text: "Gerar Relatório",
                            iconCls: true,
                            icon: "/" + global.Context + "/static/images/application-pdf.png",
                            handler: function() {
                                this.runReport("PDF", this.form.getForm());
                            },
                            scope: this
                        }
                    ]
                }
            ]
        });

        toolkit.Application.tabspace.remove(toolkit.Application.tabspace.getActiveTab());
        toolkit.Application.tabspace.add(this.panel);
        toolkit.Application.tabspace.setActiveTab(this.panel);

        toolkit.Application.tabspace.doLayout();

    }

}

toolkit.widget.ExtFileBuild = function(controller) {
    this.controller = controller;
}

toolkit.widget.ExtFileBuild.prototype = {

    builder: function(values) {
        var url = toolkit.util.Normalize.controller_action(
            this.controller,
            "builder"
        );

        url += "?" + toolkit.util.QueryBuild.build(values)
        var width  = 235;
        var height = 175;
        var left   = (screen.width - width) / 2;
        var top    = (screen.height - height) / 2;

        window.open(url, "_self");
    },

    show: function() {
        this.form = new Ext.FormPanel({
            border: false,
            items: [
                toolkit.util.Ajax.request_json(
                    "POST",
                    toolkit.util.Normalize.controller_action(
                        this.controller,
                        "action_form"
                    )
                )
            ]
        });

        this.panel = new Ext.Panel({
            title: toolkit.util.Ajax.request_json(
                "POST",
                toolkit.util.Normalize.controller_action(
                    this.controller,
                    "get_title",
                    ["TITLE"]
                )
            ).title,
            closable: true,
            items: [
                {
                    xtype: "panel",
                    bodyBorder: false,
                    width: 515,
                    style: "margin: 0 auto; padding-top: 4em",
                    title: toolkit.util.Ajax.request_json(
                                "POST",
                                toolkit.util.Normalize.controller_action(
                                    this.controller,
                                    "get_title",
                                    ["SUB_TITLE"]
                                )
                            ).title,
                    items: [
                        this.form
                    ],
                    buttonAlign: "center",
                    buttons: [
                        {
                            text: "Gerar Arquivo",
                            handler: function() {
                                this.builder(this.form.getForm().getValues());
                            },
                            scope: this
                        }
                    ]
                }
            ]
        });

        toolkit.Application.tabspace.remove(toolkit.Application.tabspace.getActiveTab());
        toolkit.Application.tabspace.add(this.panel);
        toolkit.Application.tabspace.setActiveTab(this.panel);

        toolkit.Application.tabspace.doLayout();
    }

}

toolkit.widget.TracTicket = function() {

}

toolkit.widget.TracTicket.prototype = {
    show: function() {

        this.panel = new Ext.Panel({
            activeTab: 0,
            layout: "fit",
            title: "Reportar um bug",
            style: "padding: 10pt",
            items: [
                this.createFormPanel()
            ]
        });

        toolkit.Application.tabspace.remove(toolkit.Application.tabspace.getActiveTab());
        toolkit.Application.tabspace.add(this.panel);
        toolkit.Application.tabspace.setActiveTab(this.panel);

        toolkit.Application.tabspace.doLayout();
    },

    createFormPanel: function() {

        if(this.form == undefined)
            this.form = new Ext.FormPanel({
                xtype: "formpanel",
                border: false,
                defaults: {
                    width: 550
                },
                labelWidth: 100,
                items: [
                    {
                        fieldLabel: "Versão",
                        inputType: "hidden",
                        xtype: "textfield",
                        name: "version",
                        value: toolkit.util.Ajax.request_json(
                            "POST",
                            toolkit.util.Normalize.controller_action(
                                "TracTicket",
                                "get_version"
                            )
                        )
                    },
                    {
                        fieldLabel: "Tipo",
                        name: "type",
                        inputType: "hidden",
                        xtype: "textfield",
                        value: "reported"
                    },
                    {
                        fieldLabel: "Milestone",
                        name: "milestone",
                        inputType: "hidden",
                        xtype: "textfield",
                        value: toolkit.util.Ajax.request_json(
                            "POST",
                            toolkit.util.Normalize.controller_action(
                                "TracTicket",
                                "get_milestone"
                            )
                        )
                    },
                    {
                        fieldLabel: "Título",
                        name: "title",
                        xtype: "textfield",
                        allowBlank: false
                    },
                    {
                        fieldLabel: "Descrição",
                        name: "description",
                        xtype: "textarea",
                        height: 175,
                        allowBlank: false
                    },
                ],
                buttons: [
                    {
                        text: 'Submeter',
                        handler: function() {

                            var obj = toolkit.util.Ajax.request_json(
                                "POST",
                                toolkit.util.Normalize.controller_action(
                                    "TracTicket",
                                    "create_ticket"
                                ),
                                this.form.getForm().getValues()
                            );

                            console.debug(obj);

                            if(obj.result) {
                                this.form.getForm().reset();
                                alert("Ticket submetido e pode ser acompanhado pelo protocolo (" + obj.protocol + ").");
                            }
                            else
                                alert(obj.message);

                        },
                        scope: this
                    },
                    {
                        text: "Cancelar"
                    }
                ]
            });

        return this.form;
    }
}

