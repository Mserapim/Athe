Ext.ns('toolkit.rh.ferias');


Ext.apply(
    toolkit.rh.ferias,
    {
        GerenciamentoPASUs: Ext.extend(
            Ext.Window,
            {
                commit: function () {
                    var form = this.getFormPanelUsufruto().getForm();
                    form.waitMsgTarget = this.getEl();
                    var grid = this.getGridEditorUsufruto();
                    if (grid.getStore().getCount() > 0) {
                        this.params['datas'] = new Array();
                        grid.getStore().each(function (rec) {
                            this.params['datas'].push(Array(rec.data.data_inicio.format('d/m/Y'), rec.data.data_fim.format('d/m/Y')));
                        }, this);
                    } else {
                        if (this.params.datas) delete this.params.datas;
                    }
                    form.submit({
                        waitMsg: 'Gravando dados da parcela de férias',
                        url: toolkit.util.Normalize.controller_action(
                            this.controller,
                            this.method
                        ),
                        params: this.params,
                        success: function (form, request) {
                            if (this.callback) this.callback(request.result.retorno);
                            this.params['datas'] = new Array();
                            this.destroy();
                        },
                        failure: function (form, request) {
                            if (request && request.result && request.result.error) {
                                Ext.MessageBox.show({
                                    title: 'Erro',
                                    msg: request.result.error,
                                    buttons: Ext.MessageBox.OK,
                                    icon: Ext.MessageBox.ERROR
                                });
                            } else {
                                Ext.MessageBox.show({
                                    title: 'Erro',
                                    msg: 'Ocorreu um erro enquanto gravava os dados no banco de dados.\n' +
                                        'Favor tente novamente mais tarde',
                                    buttons: Ext.MessageBox.OK,
                                    icon: Ext.MessageBox.ERROR
                                });
                            }
                            this.params['datas'] = new Array();
                        },

                        scope: this
                    });
                },

                getGridEditorUsufruto: function () {
                    if (!this.gridEditorUsufruto) {
                        var Pasu = Ext.data.Record.create([{
                            name: 'data_inicio',
                            type: 'date',
                            mapping: 'data_inicio',
                            dateFormat: 'd/m/Y',
                            altFormats: 'd/m/Y|j/n/Y|j/n/y|j/m/y|d/n/y|j/m/Y|d/m/Y|d-m-y|d-m-Y|d/m|d-m|dm|dmy|dmY|d|d-m-Y'
                        }, {
                            name: 'data_fim',
                            type: 'date',
                            mapping: 'data_fim',
                            dateFormat: 'd/m/Y',
                            altFormats: 'd/m/Y|j/n/Y|j/n/y|j/m/y|d/n/y|j/m/Y|d/m/Y|d-m-y|d-m-Y|d/m|d-m|dm|dmy|dmY|d|d-m-Y'
                        }, {
                            name: 'dias'
                        }]);

                        var pasus_data = Array();

                        var store_pasu = new Ext.data.GroupingStore({
                            reader: new Ext.data.JsonReader({ fields: Pasu }),
                            data: pasus_data,
                            sortInfo: { field: 'data_inicio', direction: 'ASC' }
                        });

                        var editor_pasu = new Ext.ux.grid.RowEditor({
                            saveText: 'Adicionar',
                            cancelText: 'Cancelar'
                        });

                        var min_value_parcela = this.pas['usufruto_ini'] ? (this.admin ? '' : this.pas['usufruto_ini']) : (new Date()).format('d/m/Y');
                        var max_value_parcela = this.pas['usufruto_fim'] ? this.pas['usufruto_fim'] : '';

                        var grid_pasu = new Ext.grid.GridPanel({
                            store: store_pasu,
                            height: 150,
                            region: 'center',
                            margins: '0 5 5 5',
                            plugins: [editor_pasu],
                            view: new Ext.grid.GroupingView({
                                markDirty: false
                            }),
                            scope: this,
                            tbar: [{
                                icon: '/' + global.Context + '/static/rh/images/add_ferias.png',
                                text: 'Adicionar parcela',
                                handler: function () {
                                    var e = new Pasu();
                                    editor_pasu.stopEditing();
                                    store_pasu.insert(0, e);
                                    grid_pasu.getView().refresh();
                                    grid_pasu.getSelectionModel().selectRow(0);
                                    editor_pasu.startEditing(0);
                                }
                            }, {
                                ref: '../removeBtn',
                                icon: '/' + global.Context + '/static/rh/images/remove_ferias.png',
                                text: 'Remover parcela',
                                disabled: true,
                                handler: function () {
                                    editor_pasu.stopEditing();
                                    var s = grid_pasu.getSelectionModel().getSelections();
                                    for (var i = 0, r; r = s[i]; i++) {
                                        store_pasu.remove(r);
                                    }
                                }
                            }],

                            columns: [
                                new Ext.grid.RowNumberer(),
                                {
                                    xtype: 'datecolumn',
                                    header: 'Início',
                                    dataIndex: 'data_inicio',
                                    format: 'd/m/Y',
                                    width: 150,
                                    sortable: true,
                                    editor: {
                                        xtype: 'datefield',
                                        allowBlank: false,
                                        minValue: min_value_parcela,
                                        minText: 'Sua parcela não pode ser anterior a ' + min_value_parcela,
                                        maxValue: max_value_parcela,
                                        invalidText: 'Data inválida!',
                                        validationEvent: false
                                    }
                                }, {
                                    xtype: 'datecolumn',
                                    header: 'Fim',
                                    dataIndex: 'data_fim',
                                    format: 'd/m/Y',
                                    width: 150,
                                    sortable: true,
                                    editor: {
                                        xtype: 'datefield',
                                        allowBlank: false,
                                        minValue: min_value_parcela,
                                        minText: 'Sua parcela não pode ser anterior a ' + min_value_parcela,
                                        maxValue: max_value_parcela,
                                        invalidText: 'Data inválida!',
                                        validationEvent: false
                                    }
                                }, {
                                    header: 'Dias',
                                    width: 50,
                                    dataIndex: 'dias',
                                    renderer: function (value, metaData, record, rowIndex, colIndex, store) {
                                        return (record.data['data_inicio'] & record.data['data_fim']) ? 1 + (record.data['data_fim'] - record.data['data_inicio']) / (1000 * 60 * 60 * 24) : '';
                                    }
                                }]
                        });
                        this.gridEditorUsufruto = grid_pasu;

                        grid_pasu.getSelectionModel().on('selectionchange', function (sm) {
                            grid_pasu.removeBtn.setDisabled(sm.getCount() < 1);
                        });
                    }

                    return this.gridEditorUsufruto;

                },

                getFormPanelUsufruto: function () {
                    if (!this.formPanelUsufruto) {
                        var buttons = [];
                        buttons = [{
                            text: 'Salvar',
                            anchor: '45%',
                            handler: this.commit,
                            scope: this
                        }, {
                            text: 'Cancelar',
                            anchor: '45%',
                            handler: this.destroy,
                            scope: this
                        }]

                        this.formPanelUsufruto = new Ext.form.FormPanel({
                            labelWidth: 80,
                            labelAlign: 'left',
                            autoHeight: true,
                            padding: 5,
                            width: 400,
                            frame: true,
                            waitMsg: 'Aguarde...',
                            items: [{
                                xtype: 'fieldset',
                                title: 'Informações sobre o período',
                                layout: 'form',
                                id: 'info_fieldset',
                                animCollapse: true,
                                collapsible: true,
                                labelWidth: 120,
                                items: [{
                                    xtype: 'panel',
                                    anchor: '100%',
                                    layout: 'column',
                                    items: [{
                                        columnWidth: .5,
                                        layout: 'form',
                                        items: [{
                                            xtype: 'displayfield',
                                            fieldLabel: 'Dias agendados',
                                            value: this.pas['dias_agendados'],
                                            anchor: '45%',
                                            name: 'dias_agendados'
                                        }]
                                    }, {
                                        columnWidth: .5,
                                        layout: 'form',
                                        items: [{
                                            xtype: 'displayfield',
                                            fieldLabel: 'Dias restantes',
                                            // value: (parseInt(this.pas['quantidade_dias'])- parseInt(this.pas['dias_marcados'])),
                                            value: this.pas['dias_nao_marcados'],
                                            anchor: '45%',
                                            name: 'dias_restantes'
                                        }]
                                    }]
                                }]
                            }, {
                                xtype: 'fieldset',
                                title: 'Justificativa',
                                collapsible: true,
                                collapsed: true, // fieldset initially collapsed
                                layout: 'hbox',
                                hidden: true,
                                id: 'info_justificativa',
                                items: [{
                                    name: 'justificativa',
                                    xtype: 'textarea',
                                    flex: 1.0,
                                    editable: true,
                                    emptyText: "Digite a justificativa para a alteração..."
                                }]
                            }, {
                                xtype: 'fieldset',
                                title: 'Publicação',
                                layout: 'form',
                                hideLabels: true,
                                collapsible: true,
                                id: 'info_publicacao',
                                hidden: true,
                                items: [{
                                    displayField: "description",
                                    value: null,
                                    hiddenName: "publicacao",
                                    valueField: "pk",
                                    width: '340',//TODO Verificar a necessidade de deixar essa width automático
                                    conf: {
                                        addLabel: "Criar ...",
                                        canAdd: true
                                    },
                                    triggerAction: "all",
                                    queryAction: "query",
                                    model: "Publicacao",
                                    hideTrigger: true,
                                    queryParam: "keyword",
                                    crudController: "RHPublicacao",
                                    xtype: "autocompletefield"
                                }]
                            }, {
                                xtype: 'fieldset',
                                title: 'Anotação',
                                layout: 'form',
                                id: 'info_anotacao',
                                defaults: {
                                    labelWidth: 300,
                                    labelAlign: 'right'
                                },
                                items: [{
                                    xtype: 'checkbox',
                                    fieldLabel: 'Gerar',
                                    name: 'anotacao',
                                    checked: true
                                }]
                            },
                            this.getGridEditorUsufruto()
                            ],
                            buttons: buttons,
                            listeners: {
                                beforeaction: function (form, act) {
                                },
                                actioncomplete: function (form, act) {
                                    this.ownerCt.destroy();
                                },
                                actionfailed: function (form, act) {
                                },
                                render: function (cmp) {
                                    cmp.getForm().waitMsgTarget = cmp.getEl();
                                }
                            }
                        });
                        this.formPanelUsufruto.getForm().waitMsgTarget = this.getEl();
                    }

                    return this.formPanelUsufruto;
                },

                getTemplateInfoPASUs: function () {
                    if (!this.templateInfoPanelPASUs) {
                        this.templateInfoPanelPASUs = new Ext.XTemplate(
                            '<p><b>Pacela(s) a ser(em) alterada(s):</b></p>',
                            '<ul style="list-style:none outside;">',
                            '<tpl for="pasus">',
                            '<li style="padding-left: 10px;"><b>>></b> {data_inicio} à {data_fim} ({dias} dias)</li>',
                            '</tpl>',
                            '</ul>',
                            '<p><b>Dias a serem alterados:</b> {dias}</p>',
                            {
                                compiled: true,
                                disableFormats: true
                            }
                        );
                    }
                    return this.templateInfoPanelPASUs;
                },

                getPublicacaoField: function () {
                    if (!this.publicacaoField) {
                        this.publicacaoField = {
                            displayField: "description",
                            fieldLabel: "Publicação",
                            value: null,
                            hiddenName: "publicacao",
                            valueField: "pk",
                            id: "publicacaoFieldCmp",
                            width: '280',//TODO Verificar a necessidade de deixar essa width automático
                            conf: {
                                addLabel: "Criar ...",
                                canAdd: true
                            },
                            triggerAction: "all",
                            queryAction: "query",
                            model: "Publicacao",
                            hideTrigger: true,
                            queryParam: "keyword",
                            crudController: "RHPublicacao",
                            xtype: "autocompletefield"
                        }
                    }
                    return this.publicacaoField;
                },

                constructor: function (pas, pasus, params) {
                    var cf = {
                        title: params['title'] + " - " + pas['periodo_aquisitivo'] || "Marcação de férias " + " - " + pas['periodo_aquisitivo'],
                        closable: true,
                        resizable: false,
                        father: params['father'] || null,
                        pas: pas,
                        admin: params['admin'] || false,
                        params: { 'pas': pas.pk, 'acao': params['acao'] || 'marcar' },
                        modal: true,
                        callback: params['callback'] || function () { },
                        controller: params['controller'] || 'FRSMarcacaoFerias',
                        method: params['method'] || 'marcacao'
                    };
                    toolkit.rh.ferias.GerenciamentoPASUs.superclass.constructor.call(this, cf);
                    this.add(this.getFormPanelUsufruto());
                    //Adicionando as parcelas a serem alteradas à informação
                    if (this.controller == 'FRSGestorFerias' & this.method == 'gerenciamento') {
                        var info_publicacao = this.findById('info_publicacao');
                        info_publicacao.show();
                        this.findById('info_justificativa').show();
                    }
                    if (this.params['acao'] == 'alterar') {
                        var info_fieldset = this.findById('info_fieldset');
                        this.findById('info_justificativa').show();
                        data = { pasus: new Array(), dias: 0 };
                        this.params['pasus'] = new Array();
                        for (i = 0; i < pasus.length; i++) {
                            data['pasus'].push(pasus[i].data);
                            data['dias'] += data['pasus'][i].dias;
                            this.params['pasus'].push(data['pasus'][i].pk);
                            info_fieldset.add({
                                xtype: 'displayfield',
                                fieldLabel: 'Parcela alterada',
                                value: pasus[i].data['data_inicio'] + ' a ' + pasus[i].data['data_fim'] + ' (' + pasus[i].data['dias'] + ' dias)',
                                anchor: '100%',
                                name: 'parcela_alterada_' + (i + 1)
                            });
                        }
                        this.pasus = data;
                    }
                }
            }
        ),

        //----------------------------------------------------------------------------
        SuspensaoPASU: Ext.extend(
            Ext.Window,
            {
                commit: function () {
                    var form = this.getFormPanel().getForm();

                    form.waitMsgTarget = this.getEl();
                    form.submit({
                        waitMsg: 'Suspendendo usufruto...',
                        url: toolkit.util.Normalize.controller_action(
                            'FRSGestorFerias',
                            'gerenciamento'
                        ),
                        params: {
                            pasu: this.configuration.pasu.pk,
                            acao: 'suspender'
                        },
                        success: function (form, request) {
                            this.configuration.callback(request.result);
                            this.destroy();
                        },
                        failure: function (form, action) {
                            if (action.result.error != undefined) {
                                alert(action.result.error);
                            } else if (action.result.result.message != undefined)
                                alert(action.result.result.message);
                            else
                                alert('Erro ao executar serviço!');
                        },
                        scope: this
                    })
                },
                getFormPanel: function () {
                    if (!this.formPanel) {
                        var today = new Date();
                        this.formPanel = new Ext.form.FormPanel({
                            frame: true,
                            border: false,
                            defaults: {
                                autoWidth: true
                            },
                            items: [{
                                xtype: 'datefield',
                                fieldLabel: 'Data Suspensão',
                                anchor: '100%',
                                name: 'data',
                                format: 'd/m/Y',
                                maxValue: this.configuration.pasu['data_fim'] ? this.configuration.pasu['data_fim'] : '',
                                value: this.configuration.pasu && toolkit.util.str2Date(this.configuration.pasu['data_inicio']) > new Date() ? Ext.util.Format.date(new Date(), 'd/m/Y') : this.configuration.pasu['data_inicio']
                            },
                            // {
                            //     displayField: "description",
                            //     fieldLabel: "Publicação",
                            //     allowBlank: false,
                            //     value: null,
                            //     width: 350,
                            //     hiddenName: "publicacao",
                            //     valueField: "pk",
                            //     conf: {
                            //         addLabel: "Criar ...",
                            //         canAdd: true
                            //     },
                            //     triggerAction: "all",
                            //     queryAction: "query",
                            //     model: "Publicacao",
                            //     hideTrigger: true,
                            //     queryParam: "keyword",
                            //     crudController: "RHPublicacao",
                            //     xtype: "autocompletefield"
                            // },
                            {
                                xtype: 'rest-autocompletefield',
                                fieldLabel: "Publicação",
                                allowBlank: true,
                                rest: "rh.publicacao.Restful",
                                name: "publicacao",
                                width: 445
                            },
                            {
                                xtype: 'fieldset',
                                title: 'Anotação',
                                layout: 'form',
                                id: 'info_anotacao',
                                defaults: {
                                    labelWidth: 300,
                                    labelAlign: 'right'
                                },
                                items: [{
                                    xtype: 'checkbox',
                                    fieldLabel: 'Gerar',
                                    name: 'anotacao',
                                    checked: true
                                }]
                            }
                            ]
                        });
                    }
                    return this.formPanel

                },
                constructor: function (father, pasu, callback) {
                    var cf = {
                        title: 'Suspensão / Interrupção de Férias',
                        closable: true,
                        resizable: false,
                        modal: true,
                        border: false,
                        width: 500,
                        configuration: {
                            pasu: pasu,
                            callback: callback || function () { }
                        },
                        buttons: [
                            {
                                text: 'Suspender',
                                scope: this,
                                handler: this.commit
                            },
                            {
                                text: 'Cancelar',
                                scope: this,
                                handler: this.destroy
                            }
                        ]
                    };
                    toolkit.rh.ferias.SuspensaoPASU.superclass.constructor.call(this, cf);

                    this.add(this.getFormPanel());
                }


            }
        ),
        //---------------------------------------------------------------------------
        GestorPASU: Ext.extend(
            Ext.Window,
            {
                addPASU: function () {
                    pas = this.configuration.pas;
                    if (pas) {
                        scope = this;
                        new toolkit.rh.ferias.GerenciamentoPASUs(
                            pas,
                            [],
                            {
                                father: this,
                                acao: 'marcar',
                                title: 'Gerenciamento de parcelas de férias',
                                callback: function (params) { scope._atualizaPanelInformation(params); },
                                controller: 'FRSGestorFerias',
                                method: 'gerenciamento',
                                admin: true
                            }
                        ).show();
                    } else {
                        Ext.MessageBox.show({
                            title: 'Erro',
                            msg: 'Houve um erro ao abrir formulário.',
                            buttons: Ext.MessageBox.OK,
                            icon: Ext.MessageBox.ERROR
                        });
                    }

                },

                editPASU: function () {
                    pas = this.configuration.pas;
                    if (pas) {
                        scope_pasu = this;
                        new toolkit.rh.ferias.GestorPASFolhaTerco(
                            this,
                            pas,
                            function (params) { scope_pasu._atualizaPanelInformation(params); }
                        ).show();
                    } else {
                        Ext.MessageBox.show({
                            title: 'Erro',
                            msg: 'Houve um erro ao abrir formulário.',
                            buttons: Ext.MessageBox.OK,
                            icon: Ext.MessageBox.ERROR
                        });
                    }

                },

                infoPASU: function () {
                    pasu = this.getGridPASU().getSelectionModel().getSelected();
                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action(
                            'FRSAutorizacaoFerias',
                            'get_info'
                        ),
                        params: { pasu: pasu.data.pk },
                        success: function (request) {
                            var result = Ext.decode(request.responseText);
                            if (result.success) {
                                new toolkit.rh.ferias.InfoPasu(
                                    result.result.pas,
                                    result.result.pasu
                                ).show();
                            } else {
                                Ext.MessageBox.show({
                                    title: 'Erro ao pesquisar parcela',
                                    msg: result.message,
                                    buttons: Ext.MessageBox.OK,
                                    icon: Ext.MessageBox.ERROR
                                });
                            }
                        },
                        failure: function (request) {
                            if (request && request.result && request.result.error) {
                                Ext.MessageBox.show({
                                    title: 'Erro de conexão',
                                    msg: request.result.error,
                                    buttons: Ext.MessageBox.OK,
                                    icon: Ext.MessageBox.ERROR
                                });
                            }
                        },
                        scope: this
                    });
                },
                desmarcarPASU: function () {
                    var scope = this;
                    var selection = this.getGridPASU().getSelectionModel();
                    pasu = selection.getSelected();
                    if (pasu) {
                        Ext.Msg.show({
                            title: 'Desmarcando Parcela de Férias',
                            msg: 'Tem certeza que deseja desmarcar a parcela selecionada?',
                            icon: Ext.Msg.QUESTION,
                            buttons: Ext.Msg.YESNO,
                            fn: function (bnt) {
                                if (bnt != 'yes') return;
                                Ext.Ajax.request({
                                    url: toolkit.util.Normalize.controller_action(
                                        'FRSGestorFerias',
                                        'gerenciamento'
                                    ),
                                    params: { acao: 'desmarcar', pas: this.configuration.pas.pk, pasu: pasu.data.pk },
                                    success: function (request) {
                                        var result = Ext.decode(request.responseText);
                                        if (result.success) {
                                            this.refreshGrid();
                                            this._atualizaPanelInformation(result.retorno);
                                            if (this.configuration.callback) this.configuration.callback();
                                        } else {
                                            Ext.MessageBox.show({
                                                title: 'Erro ao desmarcar parcela',
                                                msg: result.error,
                                                buttons: Ext.MessageBox.OK,
                                                icon: Ext.MessageBox.ERROR
                                            });
                                        }
                                    },
                                    scope: this
                                })
                            },
                            scope: this
                        });
                    }
                    else alert('Primeiro selecione a parcela que deseja desmarcar.');
                },

                alterarPASU: function () {
                    pas = this.configuration.pas;
                    pasus = this.getGridPASU().getSelectionModel().getSelections();
                    if (pasus) {
                        scope = this;
                        new toolkit.rh.ferias.GerenciamentoPASUs(
                            pas,
                            pasus,
                            {
                                father: this,
                                acao: 'alterar',
                                title: 'Solicitação de alteração de férias',
                                controller: 'FRSGestorFerias',
                                method: 'gerenciamento',
                                callback: function (params) { scope._atualizaPanelInformation(params); },
                                admin: true
                            }
                        ).show();
                    } else {
                        Ext.MessageBox.show({
                            title: 'Informação',
                            msg: 'Você deve selecionar uma parcela antes de tentar alterá-la!',
                            buttons: Ext.MessageBox.OK,
                            icon: Ext.MessageBox.INFO
                        });
                    }
                },

                suspenderPASU: function () {
                    var selection = this.getGridPASU().getSelectionModel();
                    pasu = selection.getSelected();
                    var today = new Date();
                    if (pasu) {
                        scope = this;
                        new toolkit.rh.ferias.SuspensaoPASU(
                            scope,
                            pasu.data,
                            function (result) { scope._atualizaPanelInformation(result.pas); }
                        ).show();
                    }
                    else alert('Primeiro selecione a parcela que deseja suspender.');
                },

                refreshGrid: function () {
                    this.getGridPASU().getStore().reload();
                },

                getGridPASU: function () {
                    if (!this.gridPASU) {
                        this.gridPASU = new toolkit.plugins.JsonGridPanel({
                            region: 'center',
                            cm: new Ext.grid.ColumnModel([
                                {
                                    id: 'status',
                                    dataIndex: 'status',
                                    header: '',
                                    width: 100,
                                    sortable: false,
                                    renderer: toolkit.util.formatStatus,
                                    menuDisabled: true
                                },
                                { dataIndex: 'data_inicio', header: 'Início', width: 75, sortable: false },
                                { dataIndex: 'data_fim', header: 'Fim', width: 75, sortable: false },
                                { dataIndex: 'dias', header: 'Dias', width: 50, sortable: false },
                                { dataIndex: 'situacao', header: 'Situação', width: 100, sortable: false },
                                { dataIndex: 'criado_por', header: 'Criado por', sortable: false, width: 85 },
                                { dataIndex: 'criado_em', header: 'Criado em', sortable: false, width: 85 },
                                { dataIndex: 'modificado_por', header: 'Modificado por', sortable: false, width: 85 },
                                { dataIndex: 'modificado_em', header: 'Modificado em', sortable: false, width: 85 },
                                { dataIndex: 'autorizado_em', header: 'Autorizado em', sortable: false, width: 85 },
                                { dataIndex: 'autorizado_por', header: 'Autorizado por', sortable: false, width: 120 },
                            ]),
                            sm: new Ext.grid.RowSelectionModel({ singleSelect: false }),
                            store: new Ext.data.JsonStore({
                                url: toolkit.util.Normalize.controller_action(
                                    'FRSPeriodoAquisitivoServidorUsufruto',
                                    'list'
                                ),
                                baseParams: {
                                    pas: this.configuration.pas.pk,
                                    admin: true
                                },
                                root: 'result',
                                fields: [
                                    'status',
                                    'data_inicio',
                                    'data_fim',
                                    'dias',
                                    'pk',
                                    'situacao',
                                    'criado_por',
                                    'criado_em',
                                    'modificado_por',
                                    'modificado_em',
                                    'autorizado_em',
                                    'autorizado_por',
                                ],
                                autoLoad: true,
                                listeners: {
                                    scope: this
                                }
                            }),
                            tbar: [
                                {
                                    text: 'Marcar',
                                    iconCls: true,
                                    icon: '/' + global.Context + '/static/rh/images/add_ferias.png',
                                    scope: this,
                                    handler: this.addPASU
                                },
                                {
                                    text: 'Info',
                                    iconCls: true,
                                    icon: '/' + global.Context + '/static/rh/images/remove_ferias.png',
                                    scope: this,
                                    handler: this.infoPASU
                                },
                                {
                                    text: 'Alterar',
                                    iconCls: true,
                                    icon: '/' + global.Context + '/static/rh/images/pasu_alterado.png',
                                    scope: this,
                                    handler: this.alterarPASU
                                }, '-',
                                {
                                    text: 'Suspender',
                                    iconCls: true,
                                    icon: '/' + global.Context + '/static/rh/images/suspenso.png',
                                    scope: this,
                                    handler: this.suspenderPASU
                                }, '-',
                                {
                                    text: 'Verificar Conflitos',
                                    iconCls: true,
                                    icon: '/' + global.Context + '/static/rh/images/ferias_conflito.png',
                                    scope: this,
                                    handler: this._conflitos
                                },
                                {
                                    text: 'Reenviar p/ Afastamentos',
                                    iconCls: true,
                                    icon: '/' + global.Context + '/static/rh/images/menu.png',
                                    scope: this,
                                    handler: this._reenviar
                                }

                            ]
                        });
                    }
                    return this.gridPASU;
                },

                _atualizaPanelInformation: function (params) {
                    if (params['dias_agendados'] || params['dias_agendados'] == 0) {
                        this.configuration.pas.dias_agendados = params['dias_agendados']
                        this.panelInformation.items.get('dias_agendados_field').setRawValue(params['dias_agendados']);
                    }
                    if (params['dias_usufruidos'] || params['dias_usufruidos'] == 0) {
                        this.configuration.pas.dias_usufruidos = params['dias_usufruidos']
                        this.panelInformation.items.get('dias_usufruidos_field').setRawValue(params['dias_usufruidos']);
                    }
                    if (params['situacao']) {
                        this.configuration.pas.situacao = params['situacao']
                        this.panelInformation.items.get('situacao_field').setRawValue(params['situacao']);
                    }
                    if (params['folha']) {
                        this.configuration.pas.folha_terco = params['folha'].description
                        this.configuration.pas.folha_terco_pk = params['folha'].pk
                        this.panelInformation.items.get('terco_field').setRawValue(this.configuration.pas.folha_terco);
                    }

                    this.refreshGrid();
                    if (this.configuration.callback) this.configuration.callback();

                },

                _conflitos: function () {
                    pasu = this.gridPASU.getSelectionModel().getSelected();
                    if (pasu) {
                        new toolkit.rh.ferias.ConflitosWin(
                            this,
                            [{
                                pk: pasu.data.pk,
                                conflict: pasu.data.conflict,
                                data_inicio: pasu.data.data_inicio,
                                data_fim: pasu.data.data_fim
                            }],
                            this.configuration.pas.periodo_aquisitivo_pk
                        ).show();
                    } else {
                        Ext.MessageBox.show({
                            title: 'Informação',
                            msg: 'Você deve selecionar uma parcela para verificar os conflitos!',
                            buttons: Ext.MessageBox.OK,
                            icon: Ext.MessageBox.INFO
                        });
                    }
                },

                _reenviar: function () {
                    console.debug(this.gridPASU.getSelectionModel().getSelected());
                    if (this.gridPASU.getSelectionModel().getSelected()) {
                        pasu = this.gridPASU.getSelectionModel().getSelected();
                        Ext.Ajax.request({
                            url: toolkit.util.Normalize.controller_action(
                                'FRSGestorFerias',
                                'gerenciamento'
                            ),
                            params: {
                                pasu: pasu.data.pk,
                                acao: 'reenviar'
                            },
                            success: function (request) {
                                var result = Ext.decode(request.responseText);
                                console.debug(result);
                                if (result.success) {
                                    Ext.MessageBox.show({
                                        title: 'Parcela atualizada.',
                                        msg: 'Verifique no Gestor de Afastamentos se foi criado corretamente.',
                                        buttons: Ext.MessageBox.OK,
                                        icon: Ext.MessageBox.OK
                                    });
                                } else {
                                    Ext.MessageBox.show({
                                        title: 'Erro ao reenviar parcela',
                                        msg: result.error,
                                        buttons: Ext.MessageBox.OK,
                                        icon: Ext.MessageBox.ERROR
                                    });
                                }
                            },
                            failure: function (request) {
                                if (request && request.result && request.result.error) {
                                    Ext.MessageBox.show({
                                        title: 'Erro de conexão',
                                        msg: request.result.error,
                                        buttons: Ext.MessageBox.OK,
                                        icon: Ext.MessageBox.ERROR
                                    });
                                }
                            },
                            scope: this
                        });
                    }
                    else
                        Ext.MessageBox.show({
                            title: 'Erro',
                            msg: 'Selecione uma parcela.',
                            buttons: Ext.MessageBox.OK,
                            icon: Ext.MessageBox.ERROR
                        });
                },

                getPASGridStore: function () {
                    return;
                },

                getPanelInformation: function () {
                    if (!this.panelInformation) {
                        var items = [
                            {
                                xtype: 'displayfield',
                                fieldLabel: 'Período aquisitivo',
                                anchor: '100%',
                                name: 'pa_field',
                                id: 'pa_field',
                                value: this.configuration.pas.periodo_aquisitivo || 'indefinido'
                            },
                            {
                                xtype: 'displayfield',
                                fieldLabel: 'Servidor',
                                anchor: '100%',
                                name: 'servidor_field',
                                id: 'servidor_field',
                                value: this.configuration.pas.servidor || 'indefinido'
                            },
                            {
                                xtype: 'displayfield',
                                fieldLabel: 'Dias adquiridos',
                                anchor: '100%',
                                name: 'quantidade_dias_field',
                                id: 'quantidade_dias_field',
                                value: this.configuration.pas.quantidade_dias || 0
                            },
                            {
                                xtype: 'displayfield',
                                fieldLabel: 'Dias agendados',
                                anchor: '100%',
                                name: 'dias_agendados_field',
                                id: 'dias_agendados_field',
                                value: this.configuration.pas.dias_agendados || 0
                            },
                            {
                                xtype: 'displayfield',
                                fieldLabel: 'Dias usufruídos',
                                anchor: '100%',
                                name: 'dias_usufruidos_field',
                                id: 'dias_usufruidos_field',
                                value: this.configuration.pas.dias_usufruidos || 0
                            },
                            {
                                xtype: 'displayfield',
                                fieldLabel: 'Dias indenizados',
                                anchor: '100%',
                                name: 'dias_indenizados_field',
                                id: 'dias_indenizados_field',
                                value: this.configuration.pas.paid_days || 0
                            },
                            {
                                xtype: 'displayfield',
                                fieldLabel: 'Situação',
                                anchor: '100%',
                                name: 'situacao_field',
                                id: 'situacao_field',
                                value: this.configuration.pas.situacao || 'indefinido'
                            },
                            {
                                xtype: 'displayfield',
                                fieldLabel: '1/3 Constitucional',
                                anchor: '100%',
                                name: 'terco_field',
                                id: 'terco_field',
                                value: this.configuration.pas.folha_terco || 'Não pago'
                            }
                        ];

                        this.panelInformation = new Ext.form.FieldSet({
                            title: 'Informação',
                            labelWidth: 150,
                            region: 'north',
                            width: 466,
                            height: 125,
                            autoHeight: true,
                            animCollapse: true,
                            items: items
                        });
                    }
                    return this.panelInformation;
                },

                constructor: function (pas, trigger) {
                    var cf = {
                        title: 'Gestor de Férias - Gerenciamento de parcelas',
                        width: 760,
                        height: 500,
                        closable: true,
                        resizable: true,
                        border: false,
                        layout: 'border',
                        modal: true,
                        configuration: {
                            pas: pas,
                            callback: trigger
                        }
                    };

                    toolkit.rh.ferias.GestorPASU.superclass.constructor.call(this, cf);
                    this.add(this.getPanelInformation());
                    this.add(this.getGridPASU());
                }
            }
        ),
        HomologacaoPa: Ext.extend(
            Ext.Window, {
            getFormPanel: function () {
                if (!this.formPanel) {
                    this.formPanel = new Ext.form.FormPanel({
                        timeout: 15 * 60 * 1000,
                        frame: true,
                        border: false,
                        defaults: {
                            autoWidth: true
                        },
                        items: [{
                            displayField: "description",
                            fieldLabel: "Publicação de Escala",
                            allowBlank: false,
                            value: null,
                            hiddenName: "publicacao",
                            valueField: "pk",
                            conf: {
                                addLabel: "Criar ...",
                                canAdd: true
                            },
                            triggerAction: "all",
                            queryAction: "query",
                            model: "Publicacao",
                            hideTrigger: true,
                            queryParam: "keyword",
                            crudController: "RHPublicacao",
                            xtype: "autocompletefield",
                            width: 350
                        }
                        ]
                    });
                }
                return this.formPanel;
            },
            constructor: function (pa, callback, cfg) {
                if (!cfg) cfg = {};
                var cf = {
                    title: 'Homologação - Escala de Férias ' + (cfg.title || ''),
                    closable: true,
                    resizable: false,
                    modal: true,
                    border: false,
                    width: 500,
                    configuration: {
                        pa: pa,
                        callback: callback || function () { }
                    },
                    buttons: [
                        {
                            text: 'Homologar',
                            scope: this,
                            handler: this.commit
                        },
                        {
                            text: 'Cancelar',
                            scope: this,
                            handler: this.destroy
                        }
                    ]
                };
                toolkit.rh.ferias.HomologacaoPa.superclass.constructor.call(this, cf);

                this.add(this.getFormPanel());
            },
            commit: function () {
                var form = this.getFormPanel().getForm();

                form.waitMsgTarget = this.getEl();
                form.submit({
                    waitMsg: 'Homologando Escala de Férias...',
                    url: toolkit.util.Normalize.controller_action(
                        'FRSGestorFerias',
                        'gerenciamento'
                    ),
                    params: {
                        pa: this.configuration.pa,
                        acao: 'homologar'
                    },
                    success: function (form, request) {
                        alert(request.result.result.message);
                        this.configuration.callback(request.result.result);
                        this.destroy();
                    },
                    failure: function (form, action) {
                        if (action.result.error != undefined) {
                            alert(action.result.error);
                        } else if (action.result.result.message != undefined)
                            alert(action.result.result.message);
                        else
                            alert('Erro ao executar serviço!');
                    },
                    scope: this
                })
            }
        }
        ),
        CreateOrUpdatePaServidor: Ext.extend(
            Ext.Window, {
            getFormPanel: function () {
                if (!this.formPanel) {
                    this.formPanel = new Ext.form.FormPanel({
                        frame: true,
                        border: false,
                        defaults: {
                            autoWidth: true
                        },
                        items: [{
                            displayField: "description",
                            fieldLabel: "Servidor",
                            allowBlank: false,
                            value: this.configuration.servidor || null,
                            hiddenName: "servidor",
                            valueField: "pk",
                            triggerAction: "all",
                            queryAction: "query",
                            model: "Servidor",
                            hideTrigger: true,
                            queryParam: "keyword",
                            crudController: "RHServidor",
                            xtype: "autocompletefield",
                            width: 350
                        }, {
                            displayField: "description",
                            fieldLabel: "Período Aquisitivo",
                            allowBlank: false,
                            value: this.configuration.pa || null,
                            hiddenName: "pa",
                            valueField: "pk",
                            conf: {
                                addLabel: "Criar ...",
                                canAdd: true
                            },
                            triggerAction: "all",
                            queryAction: "query",
                            model: "PeriodoAquisitivo",
                            hideTrigger: true,
                            queryParam: "keyword",
                            crudController: "FRSPeriodoAquisitivo",
                            xtype: "autocompletefield",
                            width: 350
                        }
                        ]
                    });
                }

                return this.formPanel
            },
            constructor: function (cfg, callback) {
                if (!cfg) cfg = {}
                var cf = {
                    title: 'Criação / Atualização do Período Aquisitivo do Servidor',
                    closable: true,
                    resizable: false,
                    modal: true,
                    border: false,
                    width: 500,
                    configuration: {
                        servidor: cfg.servidor || null,
                        pa: cfg.pa || null,
                        callback: callback || function () { }
                    },
                    buttons: [
                        {
                            text: 'Criar/Atualizar',
                            scope: this,
                            handler: this.commit
                        },
                        {
                            text: 'Cancelar',
                            scope: this,
                            handler: this.destroy
                        }
                    ]
                };
                toolkit.rh.ferias.CreateOrUpdatePaServidor.superclass.constructor.call(this, cf);

                this.add(this.getFormPanel());
            },

            commit: function () {
                var form = this.getFormPanel().getForm();

                form.waitMsgTarget = this.getEl();
                form.submit({
                    waitMsg: 'Criando/Atualizando Período para o servidor',
                    url: toolkit.util.Normalize.controller_action(
                        'FRSGestorFerias',
                        'gerenciamento'
                    ),
                    params: {
                        servidor: this.configuration.servidor,
                        acao: 'update_paservidor'
                    },
                    success: function (form, request) {
                        alert(request.result.result.message);
                        this.configuration.callback(request.result.result);
                        this.destroy();
                    },
                    failure: function (form, action) {
                        if (action.result.error != undefined) {
                            alert(action.result.error);
                        } else if (action.result.result.message != undefined)
                            alert(action.result.result.message);
                        else
                            alert('Erro ao executar serviço!');
                    },
                    scope: this
                })
            }
        }
        ),

        GestorFerias: Ext.extend(
            Ext.Panel,
            {
                getFilterTipoServidor: function () {
                    return '';
                },

                reload_grid: function (params) {
                    if (this.store)
                        this.store.load({
                            param: params || {}
                        });
                    else
                        alert("Bug: ExtCrud: O reload só pode ser evocado quando o grid estiver criado.");
                },

                _novoPa: function () {
                    var scope = this;
                    new toolkit.widget.ExtCrudForm(
                        {
                            controller: 'FRSPeriodoAquisitivo',
                            reload_grid: function () {
                                scope.refresh();
                            }
                        },
                        toolkit.widget.ExtCrudForm.TYPE.NEW
                    ).show();
                },

                _editarPa: function () {
                    new toolkit.widget.ExtCrudForm(
                        {
                            controller: 'FRSPeriodoAquisitivo',
                            reload_grid: function () {
                                this.refresh();
                            }
                        },
                        toolkit.widget.ExtCrudForm.TYPE.EDIT,
                        this.getSelectedPAS().data.periodo_aquisitivo_pk,
                        [
                            { 'name': 'ano_aquisicao', 'value': null, 'enabled': false },
                            { 'name': 'periodo', 'value': null, 'enabled': false },
                            { 'name': 'configuracao', 'value': null, 'enabled': false },
                            { 'name': 'mes_fruicao', 'value': null, 'enabled': false }
                        ]
                    ).show();

                },

                _homologarPa: function () {
                    var scope = this;
                    new toolkit.rh.ferias.HomologacaoPa(
                        scope.getSelectedPAS().data.periodo_aquisitivo_pk,
                        function () {
                            scope.refresh();
                        },
                        {
                            title: scope.getSelectedPAS().data.periodo_aquisitivo
                        }
                    ).show();

                },
                _liberarPa: function () {
                    if (this.getSelectionsPAS().getCount() == 1) {
                        pas = this.getSelectedPAS();
                        var pk = 0
                        if (pas.data.periodo_aquisitivo_pk) pk = pas.data.periodo_aquisitivo_pk
                        this._enviarComando({
                            row: pas,
                            controller: 'FRSGestorFerias',
                            cmd: 'gerenciamento',
                            msg: 'Tem certeza que deseja liberar este período para marcação?',
                            msg_nao_selecionado: 'Você deve selecionar um período aquisitivo antes de tentar liberá-lo!',
                            scope: this,
                            param: { acao: 'liberar', pa: pk }
                        });
                    } else {
                        Ext.MessageBox.show({
                            title: 'Informação',
                            msg: 'Você deve selecionar um (e apenas um) período aquisitivo antes de tentar liberá-lo!',
                            buttons: Ext.MessageBox.OK,
                            icon: Ext.MessageBox.INFO
                        });
                    }
                },
                _atualizarPa: function () {
                    if (this.getSelectionsPAS().getCount() == 1) {
                        pas = this.getSelectedPAS();
                        var pk = 0
                        if (pas.data.periodo_aquisitivo_pk) pk = pas.data.periodo_aquisitivo_pk
                        this._enviarComando({
                            row: pas,
                            controller: 'FRSGestorFerias',
                            cmd: 'gerenciamento',
                            msg: 'Tem certeza que deseja atualizar os servidoers para o período ' + pas.data.periodo_aquisitivo + '?',
                            msg_nao_selecionado: 'Você deve selecionar um período aquisitivo antes de tentar atualizá-lo!',
                            scope: this,
                            param: { acao: 'atualizar', pa: pk }
                        });
                    } else {
                        Ext.MessageBox.show({
                            title: 'Informação',
                            msg: 'Você deve selecionar um (e apenas um) período aquisitivo antes de tentar atualizá-lo!',
                            buttons: Ext.MessageBox.OK,
                            icon: Ext.MessageBox.INFO
                        });
                    }
                },
                createPaServidor: function () {
                    var scope = this;
                    new toolkit.rh.ferias.CreateOrUpdatePaServidor(
                        {
                            servidor: scope.getSelectedPAS() ? scope.getSelectedPAS().data.servidor_pk : null,
                            pa: scope.getSelectedPAS() ? scope.getSelectedPAS().data.periodo_aquisitivo_pk : null
                        },
                        function () {
                            scope.refresh();
                        }
                    ).show();
                },

                createAutomaticBookVacation: function () {
                    var pa = this.getSelectedPAS() ? this.getSelectedPAS().data.periodo_aquisitivo_pk : undefined;
                    var owner = this;

                    Ext.Msg.show({
                        title: 'Marcação de períodos pendentes',
                        msg: 'Tem certeza que deseja marcar férias para os servidores que não marcaram?',
                        scope: this,
                        icon: Ext.Msg.QUESTION,
                        buttons: Ext.Msg.YESNO,
                        fn: function (btn) {
                            if (btn === 'no') return;
                            owner._create(pa);
                        }
                    });
                },

                _create: function (pa) {
                    if (pa != undefined) {
                        var rest = Ext._create('rh.ferias.pas.EmployeeAcquisitionPeriodSpecialized', {});
                        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Processando...' });
                        mask.show();

                        rest.createAutomaticBookVacation(
                            pa,
                            {
                                scope: this,
                                fn: function (message) {
                                    this.responseMessage(Ext.Msg.INFO, message);
                                }
                            },
                            {
                                scope: this,
                                fn: function (message) {
                                    this.responseMessage(Ext.Msg.ERROR, message);
                                }
                            },
                            {
                                scope: this,
                                fn: function () {
                                    mask.hide();
                                }
                            }
                        );
                    }
                    else Ext.Msg.show({
                        'title': this.title,
                        'icon': Ext.Msg.ERROR,
                        'buttons': Ext.Msg.OK,
                        'msg': 'Escolha um para definir o período aquisitivo!'
                    });
                },

                responseMessage: function (icon, message) {
                    Ext.Msg.show({
                        title: 'Marcação de períodos pendentes',
                        buttons: Ext.Msg.OK,
                        icon: icon,
                        msg: message
                    });
                },

                //                createPaServidor
                getPASGridToolbar: function () {
                    if (!this.gridToolbar) {
                        var buttons = [
                            {
                                text: 'Gerenciamento - Férias',
                                iconCls: true,
                                icon: '/' + global.Context + '/static/rh/images/edit.png',
                                split: true,
                                defaultStyle: 'splitbutton',
                                menu: [
                                    this.act_gerenciarPasu,
                                    this.act_desbloquear,
                                    this.act_indenizarPas,
                                    '-',
                                    this.act_paServidor,
                                    '-',
                                    this.actAutomaticBookVacation,
                                    '-',
                                    {
                                        text: 'Período Aquisitivo',
                                        menu: [
                                            this.act_novoPa,
                                            this.act_editarPa,
                                            '-',
                                            this.act_atualizarPa,
                                            this.act_homologarPa

                                        ]

                                    }

                                ]
                            },
                            '-',
                            {
                                text: 'Ver Indenizações',
                                iconCls: true,
                                icon: '/' + global.Context + '/static/rh/images/ferias_paga.png',
                            }
                        ]

                    }
                    this.gridToolbar = this.pasGridPanel.getTopToolbar();
                    this.gridToolbar.insertButton(0, buttons);
                    return this.gridToolbar;

                },

                getPASGridPaginator: function () {
                    if (!this.pasGridPaginator) {
                        this.pasGridPaginator = new Ext.PagingToolbar({
                            store: this.getPASGridStore(),
                            displayInfo: true,
                            pageSize: 50,
                            prependButtons: true
                        })
                    }

                    return this.pasGridPaginator;
                },

                getPASColumnModel: function () {
                    if (!this.pasColumnModel) {
                        this.pasColumnModel = new Ext.grid.ColumnModel([
                            { dataIndex: 'status', id: 'status', header: 'Status', sortable: false, width: 80, renderer: toolkit.util.formatStatus },
                            { dataIndex: 'periodo_aquisitivo', header: 'Período', sortable: false, width: 120 },
                            { dataIndex: 'servidor', header: 'Servidor', sortable: false, width: 250 },
                            { dataIndex: 'quantidade_dias', header: 'Dias', sortable: false, width: 50 },
                            { dataIndex: 'dias_agendados', header: 'Agendados', sortable: false, width: 60 },
                            { dataIndex: 'dias_usufruidos', header: 'Usufruídos', sortable: false, width: 60 },
                            { dataIndex: 'dias_ausufruir', header: 'a Usufruir', sortable: false, width: 60 },
                            { dataIndex: 'paid_days', header: 'Indenizados', sortable: false, width: 60 },
                            { dataIndex: 'situacao', header: 'Situação', sortable: true, width: 250 }
                        ]);
                    }

                    return this.pasColumnModel;
                },

                getPASGridStore: function () {
                    if (!this.pasGridStore) {
                        this.pasGridStore = new Ext.data.JsonStore({
                            fields: [
                                'pk',
                                'status',
                                'servidor',
                                'servidor_pk',
                                'quantidade_dias',
                                'bloqueado',
                                'periodo_aquisitivo',
                                'periodo_aquisitivo_pk',
                                'dias_marcados',
                                'dias_agendados',
                                'dias_usufruidos',
                                'paid_days',
                                'dias_nao_marcados',
                                'dias_ausufruir',
                                'situacao',
                                'folha_terco',
                                'folha_terco_pk',
                                'usufruto_ini',
                                'usufruto_fim'
                            ],
                            root: 'result',
                            totalProperty: 'totalRows',
                            url: toolkit.util.Normalize.controller_action(this.controller, 'list'),
                            remoteSort: true,
                            listeners: {
                                scope: this,
                                load: function (st, rec, opts) {
                                    this.selectLastPASSelected();
                                }
                            }
                        });

                    }
                    return this.pasGridStore;
                },

                getPASGridPanel: function () {
                    if (!this.pasGridPanel) {
                        this.act_novoPa = new Ext.Action({
                            text: 'Novo',
                            scope: this,
                            handler: this._novoPa,
                            iconCls: true,
                            itemId: 'act_novo_pa',
                            icon: '/' + global.Context + '/static/rh/images/list-add.png'
                        });
                        this.act_editarPa = new Ext.Action({
                            text: 'Editar',
                            scope: this,
                            handler: this._editarPa,
                            iconCls: true,
                            itemId: 'act_edita_pa',
                            icon: '/' + global.Context + '/static/rh/images/edit.png',
                            disabled: true
                        });
                        this.act_atualizarPa = new Ext.Action({
                            text: 'Atualizar Servidores',
                            scope: this,
                            handler: this._atualizarPa,
                            iconCls: true,
                            itemId: 'act_atualiza_pa',
                            icon: '/' + global.Context + '/static/rh/images/edit.png',
                            disabled: true
                        });
                        this.act_homologarPa = new Ext.Action({
                            text: 'Homologar',
                            scope: this,
                            handler: this._homologarPa,
                            iconCls: true,
                            itemId: 'act_homologar_pa',
                            icon: '/' + global.Context + '/static/rh/images/pasu_homologado.png',
                            disabled: true
                        });
                        this.act_liberar = new Ext.Action({
                            text: 'Liberar',
                            scope: this,
                            handler: this._liberar,
                            iconCls: true,
                            itemId: 'act_liberar_todos',
                            icon: '/' + global.Context + '/static/rh/images/liberar_ferias.png',
                            disabled: false
                        });
                        this.act_gerenciarPasu = new Ext.Action({
                            text: 'Gerenciar parcelas',
                            scope: this,
                            handler: this._gerenciarPasu,
                            iconCls: true,
                            itemId: 'act_gerenciar_pasu',
                            icon: '/' + global.Context + '/static/rh/images/alter_ferias.png',
                            disabled: true
                        });
                        this.act_indenizarPas = new Ext.Action({
                            text: 'Indenizar período do servidor',
                            scope: this,
                            // handler: this._indenizarPas,
                            iconCls: true,
                            itemId: 'act_indenizar_pas',
                            icon: '/' + global.Context + '/static/rh/images/ferias_indenizada.png',
                            disabled: false,
                            menu: [
                                {
                                    text: 'Total',
                                    scope: this,
                                    handler: this._indenizarPas
                                },
                                {
                                    text: 'Parcial',
                                    scope: this,
                                    handler: this._indenizarPasWindow
                                }
                            ]
                        });
                        this.act_desbloquear = new Ext.Action({
                            text: 'Desbloquear',
                            scope: this,
                            handler: this._desbloquear,
                            iconCls: true,
                            itemId: 'act_desbloquear_pas',
                            icon: '/' + global.Context + '/static/rh/images/liberado.png',
                            disabled: false
                        });
                        this.act_suspenderPasu = new Ext.Action({
                            text: 'Suspender/Interromper',
                            scope: this,
                            handler: this._suspender,
                            iconCls: true,
                            itemId: 'act_suspender_pasu',
                            icon: '/' + global.Context + '/static/rh/images/suspenso.png',
                            disabled: true
                        });
                        this.act_paServidor = new Ext.Action({
                            text: 'Período Aquisitivo do Servidor',
                            scope: this,
                            handler: this.createPaServidor,
                            iconCls: true,
                            itemId: 'act_paServido',
                            icon: '/' + global.Context + '/static/rh/images/edit.png',
                        });
                        this.actAutomaticBookVacation = new Ext.Action({
                            text: 'Marcação de períodos pendentes',
                            scope: this,
                            handler: this.createAutomaticBookVacation,
                            iconCls: 'icon-core icon-core-add',
                            itemId: 'actAutomaticBookVacation',
                        });
                        this.pasGridPanel = new toolkit.plugins.JsonGridPanel({
                            searchable: true,
                            sm: new Ext.grid.RowSelectionModel({
                                singleSelect: false
                            }),
                            toSearch: [
                                { dataIndex: 'servidor', header: 'Servidor', sortable: false, width: 250 }
                            ],
                            store: this.getPASGridStore(),
                            cm: this.getPASColumnModel(),
                            flex: 1,
                            bbar: this.getPASGridPaginator(),
                            listeners: {
                                scope: this,
                                celldblclick: function (grid, rowIndex, columnIndex, e) {
                                    this._gerenciarPasu();
                                }
                            }
                        });
                    }
                    this.getPASGridToolbar();

                    return this.pasGridPanel;
                },

                getSelectedPAS: function () {
                    return this.pasGridPanel.getSelectionModel().getSelected();
                },

                getSelectionsPAS: function () {
                    return this.pasGridPanel.getSelectionModel();
                },

                getLastSelectedPAS: function () {
                    return this.pas
                },

                _enviarComando: function (params) {
                    var controller = params['controller'] || 'FRSGestorFerias';
                    var cmd = params['cmd'] || 'gerenciamento';
                    var msg = params['msg'] || 'Tem certeza que deseja executar essa operação?';
                    var msg_success_ok = params['msg_success_ok'] || '';
                    var msg_success_erro = params['msg_success_erro'] || 'Erro ao executar essa operação!';
                    var msg_nao_selecionado = params['msg_nao_selecionado'] || 'Uma linha deve ser selecionada antes de executar essa operação!';
                    var scope = params['scope'] || this;
                    var row = params['row'] || false;
                    var param = params['param'] || {};
                    if (row) {
                        Ext.MessageBox.show({
                            title: 'Atenção',
                            msg: msg,
                            fn: function (btn, text) {
                                if (btn == 'yes') {
                                    Ext.Ajax.request({
                                        url: toolkit.util.Normalize.controller_action(
                                            controller,
                                            cmd
                                        ),
                                        params: param,
                                        success: function (request) {
                                            var result = Ext.decode(request.responseText);
                                            if (result.success) {
                                                if (result.result && result.result.message)
                                                    Ext.MessageBox.show({
                                                        title: "Sucesso",
                                                        msg: result.result.message,
                                                        buttons: Ext.MessageBox.OK,
                                                        icon: Ext.MessageBox.INFO,
                                                        width: 300,
                                                    });
                                                this.refresh();
                                            } else {
                                                Ext.MessageBox.show({
                                                    title: msg_success_erro,
                                                    msg: result.error,
                                                    buttons: Ext.MessageBox.OK,
                                                    icon: Ext.MessageBox.ERROR
                                                });
                                            }
                                        },
                                        failure: function (request) {
                                            if (request && request.result && request.result.error) {
                                                Ext.MessageBox.show({
                                                    title: 'Erro de conexão',
                                                    msg: request.result.error,
                                                    buttons: Ext.MessageBox.OK,
                                                    icon: Ext.MessageBox.ERROR
                                                });
                                            }
                                        },
                                        scope: scope
                                    })

                                }
                            },
                            buttons: Ext.MessageBox.YESNO,
                            icon: Ext.MessageBox.WARNING,
                            scope: scope
                        });
                    } else {
                        Ext.MessageBox.show({
                            title: 'Informação',
                            msg: msg_nao_selecionado,
                            buttons: Ext.MessageBox.OK,
                            icon: Ext.MessageBox.INFO
                        });
                    }

                },

                _desbloquear: function () {
                    var pks = [];
                    var i = 0;
                    this.getSelectionsPAS().each(function (rec) { pks[i++] = rec.data.pk; });
                    this._enviarComando({
                        row: this.getSelectionsPAS().getCount(),
                        controller: 'FRSGestorFerias',
                        cmd: 'gerenciamento',
                        msg: 'Tem certeza que deseja alterar o bloqueio do período de férias para o(s) servidor(es) selecionado(s)?',
                        scope: this,
                        param: { acao: 'alterarbloqueio', pas: pks }
                    });
                },

                _gerenciarPasu: function () {
                    if (this.getSelectionsPAS().getCount() == 1) {
                        pas = this.getSelectedPAS();
                        var scope = this;
                        new toolkit.rh.ferias.GestorPASU(
                            pas.data,
                            function () {
                                scope.getPASGridStore().reload();
                            }
                        ).show();
                    } else {
                        var msg = 'Erro na seleção';
                        if (this.getSelectionsPAS().getCount() > 1)
                            msg = 'Você deve selecionar apenas o período de um servidor para gerenciar suas parcelas.!';
                        else
                            msg = 'Você deve selecionar um período e um servidor para gerenciar suas parcelas.!';
                        Ext.MessageBox.show({
                            title: 'Informação',
                            msg: msg,
                            buttons: Ext.MessageBox.OK,
                            icon: Ext.MessageBox.INFO
                        });
                    }
                },

                _indenizarPasWindow: function () {
                    if (this.getSelectionsPAS().getCount() == 1) {
                        var pas = this.getSelectedPAS()
                        new Ext.Window({
                            title: 'Indenizar período do servidor',
                            modal: true,
                            border: false,
                            closable: true,
                            resizable: false,
                            width: 455,
                            buttons: [
                                {
                                    text: 'Aplicar',
                                    scope: this,
                                    handler: function (b) {
                                        if ((pas.data.quantidade_dias - pas.data.paid_days - pas.data.dias_usufruidos) < b.ownerCt.ownerCt.getComponent(0).getComponent(3).getValue()) {
                                            Ext.MessageBox.show({
                                                title: 'Informação',
                                                msg: 'Quantidade de dias a indenizar maior que a quantidade de dias indenizáveis',
                                                buttons: Ext.MessageBox.OK,
                                                icon: Ext.MessageBox.INFO
                                            });
                                            return false;
                                        }
                                        else {
                                            Ext.Ajax.request({
                                                url: toolkit.util.Normalize.controller_action('FRSIndemnify', 'indemnify_vacation'),
                                                method: 'POST',
                                                scope: this,
                                                params: {
                                                    pas: pas.data.pk,
                                                    quantity: b.ownerCt.ownerCt.getComponent(0).getComponent(3).getValue(),
                                                },
                                                success: function (request) {
                                                    var obj = Ext.decode(request.responseText);
                                                    Ext.Msg.show({
                                                        title: 'Alerta',
                                                        msg: obj.message,
                                                        buttons: Ext.Msg.OK,
                                                        icon: Ext.MessageBox.WARNING
                                                    });
                                                    b.ownerCt.ownerCt.destroy();
                                                    this.getPASGridStore().reload()
                                                },
                                                failure: function (request) {
                                                    Ext.Msg.show({
                                                        title: 'Alerta',
                                                        msg: 'Ocorreu um erro na requisição. Comunique ao setor de T.I.',
                                                        buttons: Ext.Msg.OK,
                                                        icon: Ext.MessageBox.WARNING
                                                    });
                                                },
                                                waitMsg: 'Transportando informações...'
                                            });
                                        }
                                    }
                                },
                                {
                                    text: 'Cancelar',
                                    scope: this,
                                    handler: function (b) {
                                        b.ownerCt.ownerCt.destroy();
                                    }
                                }
                            ],
                            items: [
                                {
                                    xtype: 'form',
                                    frame: true,
                                    width: 450,
                                    items: [
                                        {
                                            fieldLabel: 'Servidor',
                                            xtype: 'textfield',
                                            name: 'employee',
                                            width: 320,
                                            value: pas.data.servidor,
                                            readOnly: true
                                        },
                                        {
                                            fieldLabel: 'Período',
                                            xtype: 'textfield',
                                            name: 'period',
                                            width: 320,
                                            value: pas.data.periodo_aquisitivo,
                                            readOnly: true
                                        },
                                        {
                                            fieldLabel: 'Dias indenizáveis',
                                            xtype: 'textfield',
                                            name: 'days',
                                            width: 320,
                                            value: (pas.data.quantidade_dias - pas.data.paid_days - pas.data.dias_usufruidos),
                                            readOnly: true
                                        },
                                        {
                                            fieldLabel: 'Quantidade de dias a indenizar',
                                            xtype: 'numberfield',
                                            width: 320,
                                            name: 'quantity'
                                        },
                                    ]
                                }
                            ]
                        }).show();
                    }
                    else if (this.getSelectionsPAS().getCount() > 1) {
                        Ext.MessageBox.show({
                            title: 'Informação',
                            msg: 'Você deve indenizar um período de um servidor por vez',
                            buttons: Ext.MessageBox.OK,
                            icon: Ext.MessageBox.INFO
                        });
                    } else {
                        Ext.MessageBox.show({
                            title: 'Informação',
                            msg: 'Você deve selecionar um período (PAS) de um servidor para indenizar.',
                            buttons: Ext.MessageBox.OK,
                            icon: Ext.MessageBox.INFO
                        });
                    }

                },

                _indenizarPas: function () {
                    if (this.getSelectionsPAS().getCount() >= 1) {
                        var pks = [];
                        var i = 0;
                        this.getSelectionsPAS().each(function (rec) { pks[i++] = rec.data.pk; });
                        this._enviarComando({
                            row: this.getSelectionsPAS().getCount(),
                            controller: 'FRSGestorFerias',
                            cmd: 'gerenciamento',
                            msg: 'Tem certeza que deseja indenizar do período de férias para o(s) servidor(es) selecionado(s)?',
                            scope: this,
                            param: { acao: 'indenizar', pas: pks }
                        });
                    } else {
                        var msg = 'Erro na seleção';
                        msg = 'Você deve selecionar um ou mais períodos (PAS) de um servidor para indenizar.';
                        Ext.MessageBox.show({
                            title: 'Informação',
                            msg: msg,
                            buttons: Ext.MessageBox.OK,
                            icon: Ext.MessageBox.INFO
                        });
                    }
                },

                _detalhesServidorPasu: function () {
                    var pas = this.getSelectedPAS();
                    pas.data['periodo_aquisitivo'] = this.getSelectedPA();
                    if (pas) {
                        scope = this;
                        new toolkit.rh.ferias.GestorPASFolhaTerco(
                            this,
                            pas.data,
                            function (params) { scope.getPASGridStore().reload(); }
                        ).show();
                    } else {
                        Ext.MessageBox.show({
                            title: 'Erro',
                            msg: 'Houve um erro ao abrir formulário.',
                            buttons: Ext.MessageBox.OK,
                            icon: Ext.MessageBox.ERROR
                        });
                    }
                },

                onSelectPAS: function (rec) {
                    this.pas = rec;
                    this.act_gerenciarPasu.setDisabled(false);
                    this.act_atualizarPa.setDisabled(false);
                    this.act_editarPa.setDisabled(false);
                    this.act_homologarPa.setDisabled(false);
                    this.act_paServidor.setDisabled(false);
                    this.actAutomaticBookVacation.setDisabled(false);
                    if (rec.data.bloqueado) {
                        this.act_desbloquear.setText('Desbloquear');
                    } else {
                        this.act_desbloquear.setText('Bloquear');
                    }
                },

                onDeselectPAS: function (rec) {
                    this.pas = null;
                    this.act_gerenciarPasu.setDisabled(true);
                    this.act_atualizarPa.setDisabled(true);
                    this.act_editarPa.setDisabled(true);
                    this.act_homologarPa.setDisabled(true);
                    this.act_paServidor.setDisabled(true);
                    this.actAutomaticBookVacation.setDisabled(true);
                },

                selectLastPASSelected: function () {
                    if (this.pas) {
                        idx = this.getPASGridStore().findBy(function (rec, id) { return rec.data.pk == this.pas.data.pk; }, this)
                        if (idx >= 0) this.pasGridPanel.getSelectionModel().selectRow(idx);
                    }
                },

                refresh: function () { this.getPASGridStore().reload(); },

                constructor: function (cfg) {
                    if (cfg)
                        controller = cfg.controller || 'FRSGestorFerias'
                    else controller = 'FRSGestorFerias'
                    var cf = {
                        title: 'Gestão de Férias',
                        closable: true,
                        layout: {
                            type: 'vbox',
                            padding: '5',
                            align: 'stretch'
                        },
                        defaults: { margins: '0 0 5 0' },
                        controller: controller
                    };

                    toolkit.rh.ferias.GestorFerias.superclass.constructor.call(this, cf);

                    this.add(this.getPASGridPanel());

                    var active = toolkit.Application.tabspace.getActiveTab();
                    toolkit.Application.tabspace.remove(active);
                    toolkit.Application.tabspace.add(this);
                    //--------------------------------------------------------
                    this.pasGridPanel.getSelectionModel().on(
                        "rowselect",
                        function (sm, index, rec) {
                            this.onSelectPAS(rec);
                        },
                        this
                    );
                    //-------------------------------------------------------
                }
            }
        )
    }
);


Ext.apply(
    toolkit.rh.ferias,
    {
        //----------------------------------------------------------------------------
        GestorFeriasMembros: Ext.extend(
            toolkit.rh.ferias.GestorFerias,
            {
                getFilterTipoServidor: function () {
                    return 'M';
                },
                constructor: function (cfg) {
                    var cf = {
                        controller: 'FRSGestorFeriasMembros'
                    };

                    toolkit.rh.ferias.GestorFeriasMembros.superclass.constructor.call(this, cf);
                }
            }
        ),
        //----------------------------------------------------------------------------
        GestorFeriasAdministrativo: Ext.extend(
            toolkit.rh.ferias.GestorFerias,
            {
                getFilterTipoServidor: function () {
                    return 'S';
                },
                constructor: function (cfg) {
                    var cf = {
                        controller: 'FRSGestorFeriasAdministrativo'
                    };

                    toolkit.rh.ferias.GestorFeriasAdministrativo.superclass.constructor.call(this, cf);
                }
            }
        )
        //----------------------------------------------------------------------------
    }

);

