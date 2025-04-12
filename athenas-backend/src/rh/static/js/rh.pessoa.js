
Ext.ns('toolkit.rh.pessoa');

Ext.apply(
    toolkit.rh.pessoa,
    {
        PessoaSemDocumento: Ext.extend(
        Ext.Panel,
        {
            _not_implemented: function(){ console.debug('not implemented'); },

            constructor: function(type) {
                var cf = {
                    title: 'Pessoa sem documento',
                    closable: true,
                    type: type,
                    width: 940
                };

                toolkit.rh.pessoa.PessoaSemDocumento.superclass.constructor.call(this, cf);

                var active = toolkit.Application.tabspace.getActiveTab();
                toolkit.Application.tabspace.remove(active);
                toolkit.Application.tabspace.add(this);

                this.busca = { "valor": undefined };
                this.setPessoa(undefined);
                this.setPanel(this.getPanelPesquisa());

            },

            setPanel: function(panel){
                this.removeAll();
                this.activePanel = panel;
                this.add(panel);
                this.doLayout();
            },

            setPessoa: function(pessoa){ this.pessoa = pessoa; },

            getPessoa: function(){ return this.pessoa; },

            commit: function() {
                var form = this.activePanel.getForm();
                var obj = toolkit.util.Ajax.request_json(
                    "POST",
                    toolkit.util.Normalize.controller_action(
                        "RHPessoaSemDocumento",
                        "validate",
                        ["pessoa_validate"]
                    ),
                    form.getValues()
                );
                if(obj.success){
                    form.submit({
                        clientValidation: true,
                        url: toolkit.util.Normalize.controller_action(
                            "RHPessoaSemDocumento",
                            "commit",
                            ["pessoa_commit"]
                        ),
                        params: { pessoa: this.getPessoa() ? this.getPessoa() : "" },
                        success: function(form, action){
                            if(action.result.success == true){
                                this.setPessoa(action.result.pessoa);
                                alert("Pessoa salva com sucesso!");
                            }else if(action.result) for(var i in action.result.errors) alert(action.result.errors[i]);
                        },
                        failure: function(form, action){
                            if(action.result) for(var i in action.result.errors) alert(action.result.errors[i]);
                        },
                        waitMsg: "salvando...",
                        scope: this
                    });
                }else{
                    var err = false;
                    for(var i in obj.errors) {
                        if(!isNaN(i)) {
                            var field = form.findField(obj.errors[0]);
                            if(field) {
                                field.markInvalid();
                                err = true;
                            }
                        }
                    }
                    if(err) alert("Algum campo não foi preenchido corretamente!");
                }
            },

            /*****
             *
             *    PANEL PESQUISA
             *
             **/
            getPanelPesquisa: function(){
                if(!this.panelPesquisa){
                    this.panelPesquisa = new Ext.form.FormPanel({
                        border: true,
                        width: 380,
                        title: 'Localizar Pessoa',
                        style: {
                            margin: '20px auto'
                        },
                        items:[
                            new Ext.Panel({
                                autoRender: true,
                                layout: "form",
                                border: false,
                                style: "margin: 5pt",
                                defaults: { width: 450 },
                                labelWidth: 180,
                                labelAlign: 'top',
                                items: [{
                                    width: 360,
                                    xtype: "textfield",
                                    name: "valor",
                                    enableKeyEvents: true,
                                    maxLenght: 200,
                                    fieldLabel: "Nome",
                                    listeners: {
                                        scope: this,
                                        keypress: function(el, event) {
                                            if(event.getCharCode() == 13 || event.getCharCode() == 9)
                                                this.pesquisar();
                                        }
                                    }
                                }],
                                buttons: [
                                    {
                                        text: "Pesquisar",
                                        handler: this.pesquisar,
                                        scope: this
                                    }
                                ]
                            })
                        ]
                    });
                }
                return this.panelPesquisa;
            },

            novo: function(){
                this.setPessoa(undefined);
                this.setPanelPessoa(null);
                this.setPanel(this.getPanelPessoa());
            },

            pesquisar: function(){
                this.busca['valor'] = this.getPanelPesquisa().getForm().findField("valor").getValue();
                this.setPessoa('');
                this.panelPesquisaResults = null;
                this.pessoaGridPanel = null;
                this.setPanel(this.getPessoaGridPanel());
            },

            getPessoaGridPanel: function() {
                if(!this.pessoaGridPanel) {
                    this.pessoaGridPanel = new Ext.grid.GridPanel({
                        border: false,
                        height: this.getBox().height,
                        store: this.getPessoaGridStore(),
                        cm: this.getPessoaColumnModel(),
                        sm: new Ext.grid.RowSelectionModel({ singleSelect: true }),
                        buttons: [
                            {
                                text: "Nova Pesquisa",
                                handler: this.nova_pesquisa,
                                scope: this
                            },
                            {
                                text: "Novo",
                                handler: this.novo,
                                scope: this
                            }
                        ],
                        listeners: {
                            scope: this,
                            dblclick: function() {
                                this.setPessoa(this.getPessoaGridPanel().getSelectionModel().getSelected().get("id"));
                                this.setPanelPessoa(null);
                                this.setPanel(this.getPanelPessoa());
                            }
                        }
                    });
                }

                return this.pessoaGridPanel;
            },

            getPessoaColumnModel: function() {
                return new Ext.grid.ColumnModel([
                    {
                        key: 'id',
                        header: 'Chave',
                        width: 50
                    },
                    {
                        key: 'description',
                        header: 'Nome',
                        width: 550
                    },
                    {
                        id: 'documento',
                        dataIndex: "documento",
                        header: "Status",
                        menuDisabled: true,
                        sortable: false,
                        align: 'center',
                        width: 50,
                        renderer: toolkit.util.formatStatus
                    }
                ]);
            },

            getPessoaGridPaginator: function() {
                if(!this.gridPaginator) {
                    this.gridPaginator = new Ext.PagingToolbar({
                        store: [],
                        displayInfo: true,
                        pageSize: 50,
                        prependButtons: true
                    })
                }
                return this.gridPaginator;
            },

            getPessoaGridStore: function() {
                this.gridStore = new Ext.data.JsonStore({
                    fields: ['id','description', 'documento'],
                    baseParams: {
                        valor: this.busca["valor"]
                    },
                    root: 'result',
                    totalProperty: 'totalRows',
                    url: toolkit.util.Normalize.controller_action(
                        'RHPessoaSemDocumento',
                        'pesquisa'
                    )
                });
                this.gridStore.load({params: { sort: 'id', dir: 'DESC' }});
                return this.gridStore;
            },

            nova_pesquisa: function(){
                this.busca = { "valor": undefined };
                this.panelPesquisa = null;
                this.setPanel(this.getPanelPesquisa());
            },

            /*****
             *
             *    PANEL NOVO SERVIDOR OU EDIT
             *
             **/
            setPanelPessoa: function(value){
                this.panelPessoa = value;
                this.tabDadosPessoais = value;
            },

            getDataPessoa: function(){
                if(this.getPessoa() != undefined){
                    var obj = toolkit.util.Ajax.request_json(
                            "POST",
                            toolkit.util.Normalize.controller_action(
                                "RHPessoaSemDocumento",
                                "get_data_pessoa"
                            ),
                            { pessoa: this.getPessoa() }
                    );
                    return obj;
                }else return null;
            },

            getPanelPessoa: function(){
                if(!this.panelPessoa){
                    this.store_data_pessoa = this.getDataPessoa();
                    this.panelPessoa = new Ext.form.FormPanel({
                        labelAlign: "top",
                        autoRender: true,
                        tabPosition: "top",
                        border: false,
                        frame: true,
                        height: this.getBox().height,
                        layout: 'border',
                        items: [
                            new Ext.TabPanel({
                                activeTab: 0,
                                region: 'center',
                                tabPosition: "top",
                                border: false,
                                items: [
                                    this.getTabDadosPessoais()
                                ]
                            })
                        ],
                        buttons: [
                            {
                                text: "Nova Pesquisa",
                                handler: this.nova_pesquisa,
                                scope: this
                            },
                            {
                                text: "Novo",
                                handler: this.novo,
                                scope: this
                            },
                            {
                                text: "Salvar",
                                handler: function(){this.commit();},
                                scope: this
                            }
                        ]
                    });
                }
                return this.panelPessoa;
            },

            getTabDadosPessoais: function() {
                if(!this.tabDadosPessoais){
                    this.tabDadosPessoais = new Ext.Panel({
                        title: "Dados",
                        autoRender: true,
                        border: false,
                        style: "margin: 2pt",
                        autoScroll: true,
                        region: 'center',
                        items: this.getTabDadosPessoaisFields()
                    });
                }
                return this.tabDadosPessoais;
            },

            getStore: function(store){
                var obj = toolkit.util.Ajax.request_json(
                    "POST",
                    toolkit.util.Normalize.controller_action(
                        "RHPessoaSemDocumento",
                        "get_store",
                        [store]
                    )
                );
                return obj;
            },

            getTabDadosPessoaisFields: function(){
                var column1_items = [];
                var column2_items = [];
                var width_field = 400;
                var pessoa_fisica = undefined;
                var endereco = undefined;
                var telefone = undefined;
                if(this.store_data_pessoa != null){
                    pessoa_fisica = this.store_data_pessoa.pessoa_fisica[0];
                    endereco = this.store_data_pessoa.endereco[0];
                    telefone = this.store_data_pessoa.telefone[0];
                }

                column1_items.push({
                    width: "95%",
                    name: "nome",
                    fieldLabel: "Nome",
                    xtype: "textfield",
                    value: pessoa_fisica == undefined ? "" : pessoa_fisica.nome,
                    allowBlank: false,
                    validateOnBlur: true,
                    blankText: "É necessário preencher este campo."
                });

                var f1 = new Ext.Panel({
                    layout:'column',
                    items:[{
                        columnWidth: .40,
                        layout: 'form',
                        items: [{
                            width: 100,
                            hiddenName: "sexo",
                            fieldLabel: "Sexo",
                            xtype: "combo",
                            value: pessoa_fisica == undefined ? "" : pessoa_fisica.sexo,
                            allowBlank: false,
                            validateOnBlur: true,
                            blankText: "É necessário preencher este campo.",
                            store: rh.employee.specialized.CHOICES.SEXO,
                            displayField: 'description',
                            typeAhead: true,
                            mode: "local",
                            triggerAction: 'all',
                            emptyText:'Selecione um item...',
                            selectOnFocus:true,
                            editable: true
                        }]
                    },
                    {
                        columnWidth: .40,
                        layout: 'form',
                        items: [{
                            width: 100,
                            hiddenName: "raca_cor",
                            fieldLabel: "Raça/Cor",
                            xtype: "combo",
                            value: pessoa_fisica == undefined ? "6" : pessoa_fisica.raca_cor,
                            allowBlank: false,
                            validateOnBlur: true,
                            blankText: "É necessário preencher este campo.",
                            store: rh.employee.specialized.CHOICES.RACA_COR,
                            displayField: 'description',
                            typeAhead: true,
                            mode: "local",
                            triggerAction: 'all',
                            emptyText:'Selecione um item...',
                            selectOnFocus:true,
                            editable: true
                        }]
                    }]
                });
                column1_items.push(f1);

                column1_items.push({
                    width: "95%",
                    hiddenName: "estado_civil",
                    fieldLabel: "Estado Civil",
                    xtype: "combo",
                    value: pessoa_fisica == undefined ? "1" : pessoa_fisica.estado_civil,
                    allowBlank: false,
                    validateOnBlur: true,
                    blankText: "É necessário preencher este campo.",
                    store: rh.employee.specialized.CHOICES.ESTADO_CIVIL,
                    displayField: 'description',
                    typeAhead: true,
                    mode: "local",
                    triggerAction: 'all',
                    emptyText:'Selecione um item...',
                    selectOnFocus:true,
                    editable: true
                });

                column1_items.push({
                    "width": "95%",
                    "displayField": "description",
                    "fieldLabel": "Naturalidade",
                    "allowBlank": false,
                    "hiddenName": "municipio_naturalidade",
                    "valueField": "pk",
                    "conf": {"addLabel": "Criar ...", "editLabel": "Modificar ...", "canAdd": true, "canEdit": true},
                    "triggerAction": "all",
                    "queryAction": "query",
                    "model": "Localidade",
                    "hideTrigger": true,
                    "queryParam": "keyword",
                    "crudController": "RHLocalidade",
                    "xtype": "autocompletefield",
                    "value": pessoa_fisica == undefined ? "" : pessoa_fisica.municipio_naturalidade
                });
                column1_items.push({
                    width: "95%",
                    name: "email_institucional",
                    fieldLabel: "Email institucional",
                    xtype: "textfield",
                    value: pessoa_fisica == undefined ? "" : pessoa_fisica.email_institucional,
                    allowBlank: true,
                    validateOnBlur: true,
                    blankText: "É necessário preencher este campo."
                });
                column1_items.push({
                    width: "95%",
                    name: "email_pessoal",
                    fieldLabel: "Email pessoal",
                    xtype: "textfield",
                    value: pessoa_fisica == undefined ? "" : pessoa_fisica.email_pessoal,
                    allowBlank: true,
                    validateOnBlur: true,
                    // blankText: "É necessário preencher este campo."
                });

                f1 = new Ext.Panel({
                    layout:'column',
                    items:[{
                        columnWidth:.50,
                        layout: 'form',
                        items: [{
                            name: "data_nascimento",
                            fieldLabel: "Data nascimento",
                            xtype: "datefield",
                            value: pessoa_fisica == undefined ? "" : pessoa_fisica.data_nascimento,
                            allowBlank: false,
                            validateOnBlur: true,
                            blankText: "É necessário preencher este campo."
                        }]
                    },
                    {
                        columnWidth:.50,
                        layout: 'form',
                        items: [{
                            name: "data_obito",
                            fieldLabel: "Data Óbito",
                            xtype: "datefield",
                            value: pessoa_fisica == undefined ? "" : pessoa_fisica.data_obito,
                            allowBlank: true,
                            validateOnBlur: true,
                            blankText: "É necessário preencher este campo."
                        }]
                    }]
                });
                column1_items.push(f1);

                f1 = new Ext.Panel({
                    layout:'column',
                    items:[{
                        columnWidth:.33,
                        layout: 'form',
                        items: [{
                            width: 100,
                            hiddenName: "sangue",
                            fieldLabel: "Sangue",
                            xtype: "combo",
                            value: pessoa_fisica == undefined ? "4" : pessoa_fisica.sangue,
                            allowBlank: false,
                            validateOnBlur: false,
                            blankText: "É necessário preencher este campo.",
                            store: rh.employee.specialized.CHOICES.SANGUE,
                            displayField: 'description',
                            typeAhead: true,
                            mode: "local",
                            triggerAction: 'all',
                            emptyText:'Selecione um item...',
                            selectOnFocus:true,
                            editable: true
                        }]
                    },
                    {
                        columnWidth:.33,
                        layout: 'form',
                        items: [{
                            width: 100,
                            hiddenName: "fator_rh",
                            fieldLabel: "Fator RH",
                            xtype: "combo",
                            value: pessoa_fisica == undefined ? "" : pessoa_fisica.fator_rh,
                            allowBlank: true,
                            validateOnBlur: true,
                            blankText: "É necessário preencher este campo.",
                            store: rh.employee.specialized.CHOICES.FATOR_RH,
                            displayField: 'description',
                            typeAhead: true,
                            mode: "local",
                            triggerAction: 'all',
                            emptyText:'Selecione um item...',
                            selectOnFocus:true,
                            editable: true
                        }]
                    },
                    {
                        columnWidth:.33,
                        layout: 'form',
                        items: [{
                            width: width_field,
                            name: "doador",
                            fieldLabel: "Doador",
                            xtype: "checkbox",
                            checked: pessoa_fisica == undefined ? "" : pessoa_fisica.doador,
                            allowBlank: true,
                            validateOnBlur: true,
                            blankText: "É necessário preencher este campo."
                        }]
                    }]
                });
                column1_items.push(f1);

                column1_items.push({
                    width: "95%",
                    name: "nome_pai",
                    fieldLabel: "Nome Pai",
                    xtype: "textfield",
                    value: pessoa_fisica == undefined ? "" : pessoa_fisica.nome_pai,
                    allowBlank: true,
                    validateOnBlur: true,
                    blankText: "É necessário preencher este campo."
                });
                column1_items.push({
                    width: "95%",
                    name: "nome_mae",
                    fieldLabel: "Nome Mãe",
                    xtype: "textfield",
                    value: pessoa_fisica == undefined ? "" : pessoa_fisica.nome_mae,
                    allowBlank: true,
                    validateOnBlur: true,
                    blankText: "É necessário preencher este campo."
                });
                column1_items.push({
                    name: "numero_telefone1",
                    fieldLabel: "Número de Telefone 1",
                    xtype: "fonefield",
                    allowBlank: false,
                    validateOnBlur: true,
                    blankText: "É necessário preencher este campo.",
                    value: telefone == undefined ? "" : telefone.numero_telefone1
                });
                column1_items.push({
                    name: "numero_telefone2",
                    fieldLabel: "Número de Telefone 2",
                    xtype: "fonefield",
                    allowBlank: false,
                    validateOnBlur: true,
                    blankText: "É necessário preencher este campo.",
                    value: telefone == undefined ? "" : telefone.numero_telefone2
                });

                column2_items.push({
                    width: "95%",
                    hiddenName: "tipo_endereco",
                    fieldLabel: "Tipo do Endereço",
                    xtype: "combo",
                    allowBlank: true,
                    validateOnBlur: true,
                    blankText: "É necessário preencher este campo.",
                    store: rh.employee.specialized.CHOICES.TIPO_ENDERECO,
                    displayField: 'description',
                    typeAhead: true,
                    mode: "local",
                    triggerAction: 'all',
                    emptyText:'Selecione um item...',
                    selectOnFocus:true,
                    editable: true,
                    value: endereco == undefined ? "" : endereco.tipo_endereco
                });
                column2_items.push({
                    "width": "95%",
                    "hiddenName": "municipio",
                    "fieldLabel": "Município",
                    "displayField": "description",
                    "allowBlank": true,
                    "valueField": "pk",
                    "conf": {"addLabel": "Criar ...", "editLabel": "Modificar ...", "canAdd": true, "canEdit": true},
                    "triggerAction": "all",
                    "queryAction": "query",
                    "model": "Localidade",
                    "hideTrigger": true,
                    "queryParam": "keyword",
                    "crudController": "RHLocalidade",
                    "xtype": "autocompletefield",
                    "value": endereco == undefined ? "" : endereco.municipio
                });
                column2_items.push({
                    width: "95%",
                    hiddenName: "tipo_logradouro",
                    fieldLabel: "Tipo do Logradouro",
                    xtype: "combo",
                    allowBlank: true,
                    validateOnBlur: true,
                    blankText: "É necessário preencher este campo.",
                    store: rh.employee.specialized.CHOICES.TIPO_LOGRADOURO,
                    displayField: 'description',
                    typeAhead: true,
                    mode: "local",
                    triggerAction: 'all',
                    emptyText:'Selecione um item...',
                    selectOnFocus:true,
                    editable: true,
                    value: endereco == undefined ? "" : endereco.tipo_logradouro
                });
                column2_items.push({
                    width: "95%",
                    name: "logradouro",
                    fieldLabel: "Logradouro",
                    xtype: "textfield",
                    allowBlank: true,
                    validateOnBlur: true,
                    blankText: "É necessário preencher este campo.",
                    value: endereco == undefined ? "" : endereco.logradouro
                });
                f1 = new Ext.Panel({
                    layout:'column',
                    items:[{
                        columnWidth:.50,
                        layout: 'form',
                        items: [{
                            autoWidth: true,
                            name: "numero_endereco",
                            fieldLabel: "Número",
                            xtype: "textfield",
                            allowBlank: true,
                            validateOnBlur: true,
                            blankText: "É necessário preencher este campo.",
                            value: endereco == undefined ? "" : endereco.numero
                        }]
                    },
                    {
                        columnWidth:.50,
                        layout: 'form',
                        items: [{
                            autoWidth: true,
                            name: "cep",
                            fieldLabel: "CEP",
                            xtype: "cepfield",
                            allowBlank: true,
                            validateOnBlur: true,
                            blankText: "É necessário preencher este campo.",
                            value: endereco == undefined ? "" : endereco.cep
                        }]
                    }]
                });
                column2_items.push(f1);

                column2_items.push({
                    width: "95%",
                    name: "bairro",
                    fieldLabel: "Bairro",
                    xtype: "textfield",
                    allowBlank: true,
                    validateOnBlur: true,
                    blankText: "É necessário preencher este campo.",
                    value: endereco == undefined ? "" : endereco.bairro
                });
                column2_items.push({
                    width: "95%",
                    name: "complemento",
                    fieldLabel: "Complemento",
                    xtype: "xhtmleditor",
                    height: 175,
                    allowBlank: true,
                    validateOnBlur: true,
                    blankText: "É necessário preencher este campo.",
                    value: endereco == undefined ? "" : endereco.complemento
                });

                var f = new Ext.Panel({
                    layout:'column',
                    items:[{
                            columnWidth:.5,
                            layout: 'form',
                            items: column1_items
                        }
                        ,{
                            columnWidth:.5,
                            layout: 'form',
                            items: column2_items
                        }]
                });

                setTimeout(function(){ f.doLayout(); }, 250);
                var column = [f];
                return column;
            }

        })
});