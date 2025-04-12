Ext.ns('toolkit.rh.employeespecialized');

Ext.apply(toolkit.rh.employeespecialized,
    {
        Employee: Ext.extend(Ext.Panel,
            {

                _not_implemented: function () {
                    console.debug("not implemented");
                },

                _factoryGrid: function (Class, cfg, employee) {
                    cfg = core.nullValue(cfg, {});
                    Ext.applyIf(
                        cfg,
                        {
                            servidor: employee,
                            height: 200,
                            gridAutoLoad: false
                        }
                    );
                    var grid = Ext._create(Class, cfg);
                    Ext.applyIf(
                        grid,
                        {
                            scope: this,
                            callBeforeExpand: function () {
                                var employee = this.scope.getEmployee();
                                if (employee != undefined) {
                                    this.setFilterProperty('servidor__id', employee, 100);
                                    this.setParam('servidor', employee);
                                    this.setParam('is_member', this.scope.getIsMember())
                                    this.enable();
                                }
                                else {
                                    this.removeFilterProperty('servidor__id', 100);
                                    this.setParam('servidor', undefined);
                                    this.disable();
                                }
                            }
                        }
                    );
                    return grid;
                },

                _factoryFieldSet: function (cfg, grid) {
                    grid = core.nullValue(grid, {});
                    cfg = core.nullValue(cfg, {});
                    Ext.applyIf(
                        grid,
                        {
                            callBeforeExpand: function () {
                                console.debug('_not_implemented');
                            }
                        }
                    );
                    Ext.applyIf(
                        cfg,
                        {
                            height: 250,
                            title: 'Não informado.',
                            collapsible: true,
                            collapsed: true,
                            labelAlign: 'right',
                            items: [],
                            listeners: {
                                scope: this,
                                beforeexpand: function (panel, a) {
                                    grid.callBeforeExpand();
                                },
                            },
                            scope: this,
                        }
                    );
                    var fieldset = Ext._create('Ext.form.FieldSet', cfg);
                    return fieldset;
                },

                _observeCommit: function () {
                    this._setConfigTabGrid();
                },

                _setConfigTabGrid: function () {
                    var person = this.getPerson();
                    var employee = this.getEmployee();
                    var is_member = this.getIsMember();
                    if (person != undefined) {
                        this.getTabAnotacoes().enable();
                        this.getTabMovimentacoes().enable();
                        this.getTabDependentes().enable();
                        this.getTabOutrasInformacoes().enable();
                        this.getTabHealth().enable();
                        this.getTabContacts().enable();

                        this.getSpecialNeedsField().objectId(person);
                        this.getSeriousDiseasesField().objectId(person);

                        this.getAddressGrid().setParam('person', person);
                        this.getAddressGrid().setFilterProperty('person', person, 100);

                        this.getPhoneGrid().setParam('person', person);
                        this.getPhoneGrid().setFilterProperty('person', person, 100);

                        this.getTabDocumentsGrid().enable();
                        this.getTabDocumentsGrid().setParam('naturalpersons', person);
                        this.getTabDocumentsGrid().setFilterProperty('naturalpersons__id', person, 100);

                        this.getDeficiencyInformationGrid().enable();
                        this.getDeficiencyInformationGrid().setParam('naturalperson', person);
                        this.getDeficiencyInformationGrid().setFilterProperty('naturalperson__pk', person, 100);
                    } else {
                        this.getTabAnotacoes().disable();
                        this.getTabMovimentacoes().disable();
                        this.getTabDependentes().disable();
                        this.getTabOutrasInformacoes().disable();
                        this.getTabHealth().disable();
                        this.getTabContacts().disable();

                        this.getDeficiencyInformationGrid().disable();
                        if (this.getTabDocumentsGrid())
                            this.getTabDocumentsGrid().disable();
                    }

                    if (employee != undefined) {
                        this.getDigitalDocumentsGrid().setFilterProperty('servidor__id', employee, 1001);
                        this.getDigitalDocumentsGrid().setParam('servidor', employee);
                        this.getDigitalDocumentsGrid().enable();

                        this._workplaceGrid.enable();
                        this._workassignmentGrid.enable();
                        this._concession.enable();
                        this._progression.enable();
                        this._legalframing.enable();
                        this._redistribution.enable();
                        this._requisition.enable();
                        this._removal.enable();
                        // console.debug('before setParam');
                        // console.debug(employee);
                        this.getProvisionGrid().setFilterProperty('servidor__id', employee);
                        this.getProvisionGrid().setParam('servidor', employee);
                        this.getProvisionGrid().setParam('is_member', is_member);
                        
                        // this.getProvisionGrid().enable()

                    } else {
                        this.getDigitalDocumentsGrid().disable();
                        this.getLinkToEmployeeGrid().disable();
                        this._workplaceGrid.disable();
                        this._workassignmentGrid.disable();
                        this._concession.disable();
                        this._progression.disable();
                        this._legalframing.disable();
                        this._redistribution.disable();
                        this._requisition.disable();
                        this._removal.disable();
                        // this.getProvisionGrid().disable();
                    }
                },

                constructor: function (type) {
                    var cf = {
                        title: 'Servidor',
                        closable: true,
                        type: type,
                        width: 940
                    };

                    toolkit.rh.employeespecialized.Employee.superclass.constructor.call(this, cf);

                    var active = toolkit.Application.tabspace.getActiveTab();
                    toolkit.Application.tabspace.remove(active);
                    toolkit.Application.tabspace.add(this);

                    this.busca = { "valor": undefined };
                    this.setEmployee(undefined);
                    this.setPerson(undefined);
                    this.setIsMember(undefined)
                    this.panelFoto = undefined;
                    this.setPanel(this.getPanelPesquisa());
                },

                setPanel: function (panel) {
                    this.removeAll();
                    this.activePanel = panel;
                    this.add(panel);
                    this.doLayout();
                },

                setEmployee: function (servidor) { this.servidor = servidor; },
                getEmployee: function () { return this.servidor; },

                setPerson: function (person) { this.person = person; },
                getPerson: function () { return this.person; },

                setRegistry: function (registry) { this._registry = registry; },
                getRegistry: function () { return this._registry; },

                setIsMember: function (is_member) { this.is_member = is_member; },
                getIsMember: function () { return this.is_member; },

                commit: function () {
                    var form = this.activePanel.getForm();
                    var obj = toolkit.util.Ajax.request_json(
                        "POST",
                        toolkit.util.Normalize.controller_action(
                            "RHServidorEspecializado",
                            "validate",
                            ["employee_validate"]
                        ),
                        form.getValues()
                    );
                    if (obj.success) {
                        form.submit({
                            scope: this,
                            clientValidation: true,
                            url: toolkit.util.Normalize.controller_action(
                                "RHServidorEspecializado",
                                "commit",
                                ["employee_commit"]
                            ),
                            params: { servidor: this.getEmployee() ? this.getEmployee() : "" },
                            success: function (form, action) {
                                if (action.result.servidor)
                                    this.setEmployee(action.result.servidor);
                                if (action.result.pessoa_fisica)
                                    this.setPerson(action.result.pessoa_fisica);
                                if (action.result.registry)
                                    this.setRegistry(action.result.registry);
                                if (action.result.is_member)
                                    this.setIsMember(action.result.is_member);
                                    

                                console.debug(action.result);
                                console.debug(this.getEmployee());
                                console.debug(this.getPerson());
                                console.debug(this.getRegistry());

                                this._observeCommit();

                                if (action.result.success == true) {
                                    alert("Servidor salvo com sucesso!");
                                } else {
                                    var message_err = '';
                                    var error = undefined;
                                    if (action.result) {
                                        for (var i in action.result.errors) {
                                            if (!isNaN(i)) {
                                                error = action.result.errors[i];
                                                for (var x in error) {
                                                    var field = form.findField(x);
                                                    if (field) {
                                                        field.markInvalid();
                                                        message_err += error[x] + '\n';
                                                    }
                                                    if (x == 'message_err')
                                                        message_err += error[x] + '\n';
                                                }
                                            }
                                        }
                                        if (message_err != '')
                                            alert(message_err);
                                    }
                                }
                            },
                            failure: function (form, action) {
                                var message_err = '';
                                var error = undefined;
                                if (action.result) {
                                    for (var i in action.result.errors) {
                                        if (!isNaN(i)) {
                                            error = action.result.errors[i];
                                            for (var x in error) {
                                                var field = form.findField(x);
                                                if (field) {
                                                    field.markInvalid();
                                                    message_err += error[x] + '\n';
                                                }
                                                if (x == 'message_err')
                                                    message_err += error[x] + '\n';
                                            }
                                        }
                                    }
                                    if (message_err != '')
                                        alert(message_err);
                                }
                                else alert('Campo não preenchido corretamente. Procure campos destacados em vermelho.')
                            },
                            waitMsg: "salvando..."
                        });
                    } else {
                        var message_err = '';
                        var error = undefined;
                        for (var i in obj.errors) {
                            if (!isNaN(i)) {
                                error = obj.errors[i];
                                for (var x in error) {
                                    var field = form.findField(x);
                                    if (field)
                                        field.markInvalid();
                                    if (x == 'message_err')
                                        message_err += error[x] + '\n';
                                    if (x == 'grau_instrucao' || x == 'matricula')
                                        alert("Campos da aba Dados Funcionais não informados!");
                                }
                            }
                        }
                        if (message_err != '')
                            alert(message_err);
                    }
                },

                /*****
                 *
                 *    PANEL PESQUISA
                 *
                 **/
                getPanelPesquisa: function () {
                    if (!this.panelPesquisa) {
                        this.panelPesquisa = new Ext.form.FormPanel({
                            border: true,
                            width: 380,
                            title: 'Localizar Servidor',
                            style: {
                                margin: '20px auto'
                            },
                            items: [
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
                                        // value:  "clenan",
                                        // value:  "rayson",
                                        // value:  "gustavo dettenborn",
                                        enableKeyEvents: true,
                                        maxLenght: 200,
                                        fieldLabel: "Nome ou Matrícula ou CPF",
                                        selectOnFocus: true,
                                        listeners: {
                                            scope: this,
                                            keypress: function (el, event) {
                                                if (event.getCharCode() == 13 || event.getCharCode() == 9)
                                                    this.pesquisar();
                                            },
                                            // afterrender: function(el, event) {
                                            //     this.pesquisar();
                                            // }
                                        }
                                    }],
                                    buttons: [
                                        {
                                            text: "Pesquisar",
                                            handler: this.pesquisar,
                                            scope: this
                                        },
                                        {
                                            text: "Novo",
                                            handler: this.novo,
                                            scope: this
                                        }
                                    ]
                                })
                            ]
                        });
                    }
                    return this.panelPesquisa;
                },

                novo: function () {
                    this.setEmployee(undefined);
                    this.setRegistry(undefined);
                    this.setPerson(undefined);
                    this.setPanelServidor(undefined);
                    this.gerarPanelServidor();
                },

                pesquisar: function (value) {
                    var mask = new Ext.LoadMask(this.getEl(), {
                        'msg': 'Pesquisando dados...'
                    });
                    mask.show();
                    if (value == undefined || value == '')
                        value = this.getPanelPesquisa().getForm().findField("valor").getValue();
                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action(
                            'RHServidorEspecializado', 'search'),
                        scope: this,
                        params: { valor: value },
                        success: function (request) {
                            var values = Ext.decode(request.responseText);
                            if (values.result.length == 1) {
                                mask.hide();
                                this._callEmployeeForm(values.result[0].id, values.result[0].natural_person_id, values.result[0].registry);
                            } else {
                                mask.hide();
                                this.busca = { "valor": this.getPanelPesquisa().getForm().findField("valor").getValue() };
                                this.setEmployee(undefined);
                                this.setPerson(undefined);
                                this.setRegistry(undefined);
                                this.panelFoto = undefined;
                                this.panelPesquisaResults = null;
                                this.servidorGridPanel = null;
                                this.setPanel(this.getServidorGridPanel(values));
                            }
                        },
                        failure: function (request) {
                            alert("Falha na execução da tarefa!");
                        },
                    });
                },

                getServidorGridPanel: function (data) {
                    if (!this.servidorGridPanel) {
                        this.servidorGridPanel = new Ext.grid.GridPanel({
                            border: false,
                            height: this.getBox().height,
                            store: this.getServidorGridStore(data),
                            cm: this.getServidorColumnModel(),
                            sm: new Ext.grid.RowSelectionModel({ singleSelect: true }),
                            buttons: [
                                {
                                    text: "Nova Pesquisa",
                                    handler: this.novaPesquisa,
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
                                dblclick: function () {
                                    var selected = this.getServidorGridPanel().getSelectionModel().getSelected();
                                    this._callEmployeeForm(selected.get("id"), selected.get("natural_person_id"), selected.get("registry"));
                                }
                            }
                        });
                    }
                    return this.servidorGridPanel;
                },

                _callEmployeeForm: function (employeeId, naturalPersonId, registry) {
                    this.setEmployee(employeeId);
                    this.setPerson(naturalPersonId);
                    this.setRegistry(registry);
                    this.setPanelServidor(undefined);
                    this.gerarPanelServidor();
                },

                getServidorColumnModel: function () {
                    return new Ext.grid.ColumnModel([
                        {
                            key: 'id',
                            dataIndex: 'id',
                            header: 'Chave',
                            width: 50
                        },
                        {
                            key: 'description',
                            dataIndex: 'description',
                            header: 'Nome',
                            width: 550
                        },
                        {
                            align: 'center',
                            header: 'Ativo',
                            key: 'status',
                            dataIndex: 'status',
                            id: 'status',
                            width: 70,
                            menuDisabled: true,
                            renderer: toolkit.util.formatStatus
                        }
                    ]);
                },

                getServidorGridPaginator: function () {
                    if (!this.gridPaginator) {
                        this.gridPaginator = new Ext.PagingToolbar({
                            store: [],
                            displayInfo: true,
                            pageSize: 50,
                            prependButtons: true
                        });
                    }
                    return this.gridPaginator;
                },

                getServidorGridStore: function (data) {
                    this.gridStore = new Ext.data.JsonStore({
                        fields: ['id', 'description', 'status'],
                        baseParams: {
                            valor: this.busca["valor"]
                        },
                        root: 'result',
                        totalProperty: 'totalRows',
                        url: toolkit.util.Normalize.controller_action(
                            'RHServidorEspecializado',
                            'search'
                        )
                    });
                    if (data.result.length > 0)
                        this.gridStore.loadData(data);
                    else
                        this.gridStore.load({ params: { sort: 'id', dir: 'DESC' } });
                    return this.gridStore;
                },

                novaPesquisa: function () {
                    this.busca = { "valor": undefined };

                    this._tabDocumentsGrid = null;
                    this.tabContacts = null;
                    this._tabHealth = null;
                    this._specialNeedsField = null;
                    this._seriousDiseasesField = null;
                    this._deficiencyInformationGrid = null;
                    this._phoneGrid = null;
                    this._addressGrid = null;
                    this._dependentGrid = null;
                    this._dependencyGrid = null;
                    this.panelPesquisa = null;
                    this._gridDigitalDocuments = null;
                    this._linkToEmployeeGrid = null;

                    if (this.panelServidor) this.panelServidor.destroy();

                    this.setPanel(this.getPanelPesquisa());
                },

                /*****
                 *
                 *    PANEL NOVO SERVIDOR OU EDIT
                 *
                 **/
                setPanelServidor: function (value) {
                    if (this.panelFoto != undefined)
                        this.panelFoto.removeAll();
                    if (this.panelServidor != undefined)
                        this.panelServidor.removeAll();
                    if (this.tabDadosPessoais != undefined)
                        this.tabDadosPessoais.removeAll();
                    if (this.gridPanelFolhas != undefined)
                        this.gridPanelFolhas.removeAll();
                    if (this.tabDadosFuncionais != undefined)
                        this.tabDadosFuncionais.removeAll();
                    if (this.tabOutrasInformacoes != undefined)
                        this.tabOutrasInformacoes.removeAll();
                    if (this.tabMovimentacoes != undefined)
                        this.tabMovimentacoes.removeAll();
                    if (this.abaProvimentos != undefined)
                        this.abaProvimentos.removeAll();
                    if (this.tabAnotacoes != undefined)
                        this.tabAnotacoes.removeAll();
                    if (this.tabDependentes != undefined)
                        this.tabDependentes.removeAll();
                    if (this.tabFormacao != undefined)
                        this.tabFormacao.removeAll();

                    this.panelFoto = value;
                    this.panelServidor = value;
                    this.tabDadosPessoais = value;
                    this.gridPanelFolhas = value;
                    this.tabDadosFuncionais = value;
                    this.tabOutrasInformacoes = value;
                    this.tabMovimentacoes = value;
                    this.abaProvimentos = value;
                    this.tabAnotacoes = value;
                    this.tabDependentes = value;
                    this.tabFormacao = value;
                    this._civilStatus = value;
                    this._degreeEducationChoiceField = value;
                },

                gerarPanelServidor: function () {
                    var mask = new Ext.LoadMask(this.getEl(), {
                        'msg': 'Carregando dados...'
                    });
                    mask.show();

                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action(
                            'RHServidorEspecializado', 'get_data_employee'),
                        method: 'POST',
                        success: function (request) {
                            var values = Ext.decode(request.responseText);
                            this.setPanel(this.getPanelServidor(values));
                            mask.hide();
                        },
                        failure: function (request) {
                            mask.hide();
                            alert("Falha na execução da tarefa!");
                        },
                        scope: this,
                        params: { servidor: this.getEmployee() }
                    });
                },

                getPanelServidor: function (store_data_servidor) {
                    if (!this.panelServidor) {
                        this.store_data_servidor = store_data_servidor;
                        this.setPerson(this.store_data_servidor.pessoa_fisica.pk);
                        this.panelServidor = new Ext.form.FormPanel({
                            autoWidth: true,
                            labelAlign: 'top',
                            autoRender: true,
                            tabPosition: 'top',
                            border: false,
                            frame: true,
                            height: this.getBox().height,
                            layout: 'border',
                            items: [
                                new Ext.Panel({
                                    title: (
                                        this.store_data_servidor.servidor.matricula + ' ' +
                                        this.store_data_servidor.pessoa_fisica.nome + ' | ' +
                                        'Situação Funcional: ' + this.store_data_servidor.dados_estaticos_informacoes.situacao_funcional + ' | ' +
                                        'Categoria: ' + this.store_data_servidor.dados_estaticos_informacoes.categoria),
                                    region: 'north'
                                }),
                                new Ext.TabPanel({
                                    activeTab: 0,
                                    region: 'center',
                                    tabPosition: 'top',
                                    border: false,
                                    items: [
                                        this.getTabDadosPessoais(),
                                        this.getTabDadosFuncionais(),
                                        this.getTabDocumentsGrid(),
                                        this.getTabContacts(),
                                        this.getTabHealth(),
                                        this.getTabOutrasInformacoes(),
                                        this.getTabDependentes(),
                                        this.getTabMovimentacoes(),
                                        // this.getAbaProvimentos(),
                                        this.getProvisionGrid(),
                                        this.getTabAnotacoes(),
                                        this.getTabFormacao()
                                    ]
                                })
                            ],
                            buttons: [
                                {
                                    text: "Nova Pesquisa",
                                    handler: this.novaPesquisa,
                                    scope: this
                                },
                                {
                                    text: "Novo",
                                    handler: this.novo,
                                    scope: this
                                },
                                {
                                    text: "Salvar",
                                    handler: function () {
                                        var tpanel = this.getTabDadosFuncionais().ownerCt;
                                        var active = tpanel.getActiveTab();

                                        tpanel.setActiveTab(this.getTabDadosFuncionais());
                                        tpanel.setActiveTab(active);
                                        this.commit();
                                    },
                                    scope: this
                                }
                            ],
                            listeners: {
                                scope: this,
                                afterrender: function (layout) {
                                    this._setConfigTabGrid();
                                }
                            }
                        });
                    }
                    return this.panelServidor;
                },

                getTabDependentes: function () {
                    if (!this.tabDependentes) {
                        this.tabDependentes = new Ext.Panel({
                            title: "Dependentes/Vínculos",
                            autoRender: true,
                            border: false,
                            style: 'margin: 2pt',
                            autoScroll: true,
                            region: 'center',
                            items: this.getTabDependentesFields(),
                            listeners: {
                                scope: this,
                                beforeshow: function (panel) {
                                    try { if (!this.tabDependentes.layout_show) this.activePanel.doLayout(); }
                                    catch (e) { console.debug(e); }
                                },
                                afterlayout: function (layout) { this.tabDependentes.layout_show = true; }
                            }
                        });
                        this.tabDependentes.layout_show = false;
                    }
                    return this.tabDependentes;
                },

                getLinkToEmployeeGrid: function () {
                    if (this._linkToEmployeeGrid == undefined) {
                        this._linkToEmployeeGrid = this._factoryGrid('rh.employee.linktoemployee.Grid', {
                            servidor: this.getEmployee(),
                            height: 200,
                        },
                            this.getEmployee()
                        );
                    }
                    return this._linkToEmployeeGrid;
                },

                getTabDependentesFields: function () {
                    var linktoemployee = this.getLinkToEmployeeGrid();
                    var items = [
                        this._factoryFieldSet(
                            {
                                title: 'Dependentes/Dependências',
                                height: 450,
                                items: [
                                    this.getDependentGrid(),
                                    this.getDependencyGrid(),
                                ]
                            },
                            this.getDependentGrid()
                        ),
                        this._factoryFieldSet({ title: 'Vínculo com servidores', items: [linktoemployee], height: 250 }, linktoemployee),
                    ];
                    return items;
                },

                observeDependente: function () {
                    if (this.dependente()) {
                        this.getDependencyGrid().enable();
                        this.getDependencyGrid().setParam('dependente', this.dependente());
                        this.getDependencyGrid().setFilterProperty('dependente_id', this.dependente(), 100);
                    }
                    else {
                        this.getDependencyGrid().disable();
                        this.getDependencyGrid().getStore().removeAll();
                        this.getDependencyGrid().setFilterProperty('dependente_id', 0, 100, false);
                    }
                },

                dependente: function (value, dispatch) {
                    dispatch = core.nullValue(dispatch, true);

                    if (value !== undefined) {
                        this._dependente = value;

                        if (dispatch) this.observeDependente();
                    }
                    else
                        return this._dependente;
                },

                getDependentGrid: function (cfg) {
                    if (!this._dependentGrid) {
                        this._dependentGrid = Ext._create('rh.dependente.DependenteGrid', {
                            hideItemsToolbar: ['search', 'download'],
                            title: 'Dependentes',
                            region: 'center',
                            border: false,
                            scope: this,
                            height: 200,
                            gridAutoLoad: false,
                            columnAction: false,
                            hideColumns: [
                                'unicode',
                                'auxilio_creche',
                                'data_alteracao',
                                'data_fim',
                                'motivo_inicio_dependencia',
                                'motivo_inicio_dependencia_display',
                                'motivo_fim_dependencia',
                                'motivo_fim_dependencia_display',
                                'data_cadastro',
                                'dep_ir',
                                'data_inicio',
                                'dep_sf',
                                'dependente_direto',
                                'responsavel_unicode',
                            ]
                        });
                        this._dependentGrid.getSelectionModel().on({
                            scope: this,
                            rowselect: function (sm, index, data) {
                                this.dependente(data.get('pk'));
                            },
                            rowdeselect: function () {
                                this.dependente(null);
                            },
                        });
                        this._dependentGrid.getStore().on({
                            scope: this,
                            load: function (gd, opts) {
                                var selection = this._dependentGrid.getSelectionModel();
                                var rec = selection.getSelected();
                                this.dependente(null);
                                if (rec) {
                                    selection.clearSelections();
                                    selection.selectRecords([rec]);
                                }

                            }
                        });
                        var grid = this._dependentGrid;
                        this._dependentGrid.callBeforeExpand = function () {
                            var employee = this.scope.getEmployee();
                            if (employee != undefined) {
                                this.setFilterProperty('servidor', employee, 100);
                                this.setParam('servidor', employee);
                                this.enable();
                            }
                            else
                                this.disable();
                        }
                    }
                    return this._dependentGrid;
                },

                getDependencyGrid: function (cfg) {
                    if (!this._dependencyGrid) {
                        this._dependencyGrid = Ext._create('rh.dependente.DependenciaGrid', {
                            hideItemsToolbar: ['search', 'download'],
                            title: 'Dependência',
                            region: 'center',
                            border: false,
                            scope: this,
                            height: 200,
                            columnAction: false,
                            style: "margin-top: 10pt",
                            gridAutoLoad: false,
                            hideColumns: [
                                'unicode',
                            ]
                        });
                    }
                    return this._dependencyGrid;
                },

                getTabDadosPessoais: function () {
                    if (!this.tabDadosPessoais) {
                        this.mask = new Ext.LoadMask(this.getEl(), {
                            'msg': 'Carregando dados...'
                        });
                        this.mask.show();
                        this.tabDadosPessoais = new Ext.Panel({
                            title: "Dados Pessoais",
                            autoRender: true,
                            border: false,
                            style: 'margin: 2pt',
                            autoScroll: true,
                            region: 'center',
                            items: this.getTabDadosPessoaisFields(),
                            listeners: {
                                scope: this,
                                beforeshow: function (panel) {
                                    try { if (!this.tabDadosPessoais.layout_show) this.activePanel.doLayout(); }
                                    catch (e) { console.debug(e); }
                                },
                                afterlayout: function (layout) {
                                    this.mask.hide();
                                    this.tabDadosPessoais.layout_show = true;
                                }
                            }
                        });
                        this.tabDadosPessoais.layout_show = false;
                    }
                    return this.tabDadosPessoais;
                },

                getStore: function (store) {
                    var obj = toolkit.util.Ajax.request_json(
                        "POST",
                        toolkit.util.Normalize.controller_action(
                            "RHServidorEspecializado",
                            "get_store",
                            [store]
                        )
                    );
                    return obj;
                },

                getPanelFoto: function (link) {
                    if (!this.panelFoto) {
                        this.panelFoto = new Ext.Panel({
                            id: 'foto-view',
                            width: 85,
                            height: 120,
                            html: '<div><img src="' + link + '" alt="Visualização da foto" /></div>'
                        });
                    }
                    return this.panelFoto;
                },

                getCivilStatusField: function (cfg) {
                    if (!this._civilStatus) {
                        cfg = cfg || {};
                        Ext.applyIf(cfg, {
                            fieldLabel: 'Estado civil',
                            hiddenName: 'estado_civil',
                            choiceId: 'rh.MARITAL_STATUS',
                            width: 350
                        });
                        this._civilStatus = Ext._create('standard.fields.ChoiceField', cfg);
                        var store = this._civilStatus.getStore();
                        var filter = Ext.decode(store.baseParams.filter);
                        filter.push({ property: 'value__in', value: [7], stage: -1 });
                        store.baseParams.filter = Ext.encode(filter);
                        store.load();
                    }
                    return this._civilStatus;
                },

                getTabDadosPessoaisFields: function () {
                    var column1_items = [];
                    var column2_items = [];
                    var width_field = 400;
                    var pessoa_fisica = this.store_data_servidor.pessoa_fisica;
                    var documento = this.store_data_servidor.documento;

                    column1_items.push({
                        width: "95%",
                        name: "nome",
                        fieldLabel: "Nome",
                        xtype: "textfield",
                        value: pessoa_fisica.nome,
                        allowBlank: false,
                        validateOnBlur: true,
                        blankText: "É necessário preencher este campo."
                    });

                    column1_items.push({
                        width: "95%",
                        name: "social_name",
                        fieldLabel: "Nome social",
                        xtype: "textfield",
                        value: pessoa_fisica.social_name,
                        allowBlank: true,
                        validateOnBlur: true,
                        blankText: "É necessário preencher este campo."
                    });

                    var f1 = new Ext.Panel({
                        layout: 'column',
                        items: [{
                            columnWidth: ".40",
                            layout: 'form',
                            items: [{
                                width: 100,
                                name: "sexo",
                                hiddenName: "sexo",
                                fieldLabel: "Sexo",
                                xtype: "combo",
                                value: pessoa_fisica.sexo,
                                allowBlank: false,
                                validateOnBlur: true,
                                blankText: "É necessário preencher este campo.",
                                store: rh.employee.specialized.CHOICES.SEXO,
                                displayField: 'description',
                                typeAhead: true,
                                mode: "local",
                                triggerAction: 'all',
                                emptyText: 'Selecione um item...',
                                selectOnFocus: true,
                                editable: true
                            }]
                        },
                        {
                            columnWidth: ".40",
                            layout: 'form',
                            items: [{
                                fieldLabel: 'Raça/Cor',
                                xtype: 'choicefield',
                                hiddenName: 'raca_cor',
                                choiceId: 'rh.TYPE_RACE',
                                width: 100,
                                value: pessoa_fisica.raca_cor == "" ? "5" : pessoa_fisica.raca_cor,
                            }]
                        }]
                    });
                    column1_items.push(f1);

                    var f1 = new Ext.Panel({
                        layout: 'column',
                        items: [{
                            columnWidth: ".40",
                            layout: 'form',
                            items: [{
                                fieldLabel: 'Orientação Sexual',
                                xtype: 'choicefield',
                                hiddenName: 'sexual_orientation',
                                choiceId: 'rh.SEXUAL_ORIENTATION',
                                value: pessoa_fisica.sexual_orientation == "" ? "5" : pessoa_fisica.sexual_orientation,
                                width: 100,
                            }]
                        }]
                    });
                    column1_items.push(f1);

                    column1_items.push(this.getCivilStatusField({ value: pessoa_fisica.estado_civil ? pessoa_fisica.estado_civil : 1 }));

                    column1_items.push({
                        width: 350,
                        displayField: "description",
                        fieldLabel: "Naturalidade",
                        allowBlank: false,
                        hiddenName: "municipio_naturalidade",
                        valueField: "pk",
                        conf: { "addLabel": "Criar ...", "editLabel": "Modificar ...", "canAdd": true, "canEdit": true },
                        triggerAction: "all",
                        queryAction: "query",
                        model: "Localidade",
                        hideTrigger: true,
                        queryParam: "keyword",
                        crudController: "RHLocalidade",
                        xtype: "autocompletefield",
                        value: pessoa_fisica.municipio_naturalidade
                    });
                    column1_items.push({
                        width: "95%",
                        name: "email_institucional",
                        fieldLabel: "Email institucional",
                        xtype: "textfield",
                        value: pessoa_fisica.email_institucional,
                        allowBlank: true,
                        validateOnBlur: true,
                        blankText: "É necessário preencher este campo."
                    });
                    column1_items.push({
                        width: "95%",
                        name: "email_pessoal",
                        fieldLabel: "Email pessoal",
                        xtype: "textfield",
                        value: pessoa_fisica.email_pessoal,
                        allowBlank: true,
                        validateOnBlur: true,
                        // blankText: "É necessário preencher este campo."
                    });

                    f1 = new Ext.Panel({
                        layout: 'column',
                        items: [{
                            columnWidth: ".50",
                            layout: 'form',
                            items: [{
                                name: "data_nascimento",
                                fieldLabel: "Data nascimento",
                                xtype: "datefield",
                                value: pessoa_fisica.data_nascimento,
                                allowBlank: false,
                                validateOnBlur: true,
                                blankText: "É necessário preencher este campo."
                            }]
                        },
                        {
                            columnWidth: ".50",
                            layout: 'form',
                            items: [{
                                name: "data_obito",
                                fieldLabel: "Data Óbito",
                                xtype: "datefield",
                                value: pessoa_fisica.data_obito,
                                allowBlank: true,
                                validateOnBlur: true,
                                blankText: "É necessário preencher este campo."
                            }]
                        }]
                    });
                    column1_items.push(f1);

                    f1 = new Ext.Panel({
                        layout: 'column',
                        items: [{
                            columnWidth: ".33",
                            layout: 'form',
                            items: [{
                                width: 100,
                                hiddenName: "sangue",
                                fieldLabel: "Sangue",
                                xtype: "combo",
                                value: pessoa_fisica.sangue ? pessoa_fisica.sangue : 4,
                                allowBlank: true,
                                validateOnBlur: true,
                                blankText: "É necessário preencher este campo.",
                                store: rh.employee.specialized.CHOICES.SANGUE,
                                displayField: 'description',
                                typeAhead: true,
                                mode: "local",
                                triggerAction: 'all',
                                emptyText: 'Selecione um item...',
                                selectOnFocus: true,
                                editable: true
                            }]
                        },
                        {
                            columnWidth: ".33",
                            layout: 'form',
                            items: [{
                                width: 100,
                                hiddenName: "fator_rh",
                                fieldLabel: "Fator RH",
                                xtype: "combo",
                                value: pessoa_fisica.fator_rh ? pessoa_fisica.fator_rh : 2,
                                allowBlank: true,
                                validateOnBlur: true,
                                blankText: "É necessário preencher este campo.",
                                store: rh.employee.specialized.CHOICES.FATOR_RH,
                                displayField: 'description',
                                typeAhead: true,
                                mode: "local",
                                triggerAction: 'all',
                                emptyText: 'Selecione um item...',
                                selectOnFocus: true,
                                editable: true
                            }]
                        },
                        {
                            columnWidth: ".33",
                            layout: 'form',
                            items: [{
                                width: width_field,
                                name: "doador",
                                fieldLabel: "Doador",
                                xtype: "checkbox",
                                checked: pessoa_fisica.doador,
                                allowBlank: true,
                                validateOnBlur: true,
                                blankText: "É necessário preencher este campo."
                            }]
                        }]
                    });
                    column2_items.push(f1);

                    column2_items.push({
                        width: "95%",
                        name: "nome_pai",
                        fieldLabel: "Nome Pai",
                        xtype: "textfield",
                        value: pessoa_fisica.nome_pai,
                        allowBlank: true,
                        validateOnBlur: true,
                        blankText: "É necessário preencher este campo."
                    });
                    column2_items.push({
                        width: "95%",
                        name: "nome_mae",
                        fieldLabel: "Nome Mãe",
                        xtype: "textfield",
                        value: pessoa_fisica.nome_mae,
                        allowBlank: true,
                        validateOnBlur: true,
                        blankText: "É necessário preencher este campo."
                    });
                    column2_items.push({
                        width: "95%",
                        name: "nome_conjuge",
                        fieldLabel: "Nome Cônjuge",
                        xtype: "textfield",
                        value: pessoa_fisica.nome_conjuge,
                        allowBlank: true,
                        validateOnBlur: true,
                        blankText: "É necessário preencher este campo."
                    });
                    column1_items.push({
                        width: "95%",
                        name: "cpf",
                        fieldLabel: "CPF",
                        xtype: "cpffield",
                        value: pessoa_fisica.cpf,
                        allowBlank: false,
                        validateOnBlur: true,
                        blankText: "É necessário preencher este campo."
                    });
                    column1_items.push({
                        width: "95%",
                        name: "rg",
                        fieldLabel: "RG",
                        xtype: "textfield",
                        value: pessoa_fisica.rg,
                        allowBlank: false,
                        validateOnBlur: true,
                        blankText: "É necessário preencher este campo."
                    });

                    f1 = new Ext.Panel({
                        layout: 'column',
                        items: [{
                            columnWidth: ".50",
                            layout: 'form',
                            items: [{
                                autoWidth: true,
                                name: "rg_orgao",
                                fieldLabel: "RG Órgão",
                                xtype: "textfield",
                                value: pessoa_fisica.rg_orgao,
                                allowBlank: false,
                                validateOnBlur: true,
                                blankText: "É necessário preencher este campo."
                            }]
                        },
                        {
                            columnWidth: ".50",
                            layout: 'form',
                            items: [{
                                name: "rg_data_expedicao",
                                fieldLabel: "RG Data Expedição",
                                xtype: "datefield",
                                value: pessoa_fisica.rg_data_expedicao,
                                allowBlank: false,
                                validateOnBlur: true,
                                blankText: "É necessário preencher este campo."
                            }]
                        }]
                    });
                    column1_items.push(f1);

                    column1_items.push({
                        width: 350,
                        hiddenName: "rg_uf",
                        fieldLabel: "RG UF",
                        xtype: "combo",
                        value: pessoa_fisica.rg_uf,
                        allowBlank: false,
                        validateOnBlur: true,
                        blankText: "É necessário preencher este campo.",
                        store: this.getStore("estado"),
                        displayField: 'description',
                        typeAhead: true,
                        mode: "local",
                        triggerAction: 'all',
                        emptyText: 'Selecione um item...',
                        selectOnFocus: true,
                        editable: true
                    });

                    f1 = new Ext.Panel({
                        layout: 'column',
                        scope: this,
                        items: [{
                            columnWidth: ".50",
                            layout: 'form',
                            scope: this,
                            items: [
                                {
                                    name: "foto",
                                    fieldLabel: "Foto",
                                    xtype: "ged-imageuploadfield",
                                    types: ['image/jpeg', 'image/png'],
                                    allowBlank: true,
                                    validateOnBlur: true,
                                    blankText: "É necessário preencher este campo.",
                                    value: pessoa_fisica.foto,
                                    scope: this
                                },
                                {
                                    columnWidth: ".50",
                                    layout: 'form',
                                    items: this.getPanelFoto(pessoa_fisica.foto_link)
                                },
                                {
                                    autoWidth: true,
                                    name: "ric",
                                    fieldLabel: "RIC",
                                    xtype: "textfield",
                                    allowBlank: true,
                                    validateOnBlur: true,
                                    blankText: "",
                                    value: documento.ric
                                },
                                {
                                    name: "ric_expedition_date",
                                    fieldLabel: "RIC - Data de Expedição",
                                    xtype: "datefield",
                                    value: documento.ric_expedition_date,
                                    allowBlank: true,
                                    validateOnBlur: true,
                                    blankText: ""
                                },
                                {
                                    name: "ric_issuer",
                                    fieldLabel: "RIC - Órgão emissor",
                                    xtype: "textfield",
                                    value: documento.ric_issuer,
                                    allowBlank: true,
                                    validateOnBlur: true,
                                    blankText: ""
                                },
                                {
                                    width: 350,
                                    hiddenName: "ric_state",
                                    fieldLabel: "RIC - UF",
                                    xtype: "combo",
                                    value: documento.ric_state,
                                    allowBlank: true,
                                    validateOnBlur: true,
                                    blankText: "",
                                    store: this.getStore("estado"),
                                    displayField: 'description',
                                    typeAhead: true,
                                    mode: "local",
                                    triggerAction: 'all',
                                    emptyText: 'Selecione um item...',
                                    selectOnFocus: true,
                                    editable: true
                                },
                                {
                                    autoWidth: true,
                                    name: "rne",
                                    fieldLabel: "RNE",
                                    xtype: "textfield",
                                    allowBlank: true,
                                    validateOnBlur: true,
                                    blankText: "",
                                    value: documento.rne
                                },
                                {
                                    name: "rne_expedition_date",
                                    fieldLabel: "RNE - Data de Expedição",
                                    xtype: "datefield",
                                    value: documento.rne_expedition_date,
                                    allowBlank: true,
                                    validateOnBlur: true,
                                    blankText: ""
                                },
                                {
                                    name: "rne_issuer",
                                    fieldLabel: "RNE - Órgão emissor",
                                    xtype: "textfield",
                                    value: documento.rne_issuer,
                                    allowBlank: true,
                                    validateOnBlur: true,
                                    blankText: ""
                                },
                                {
                                    width: 350,
                                    hiddenName: "rne_state",
                                    fieldLabel: "RNE - UF",
                                    xtype: "combo",
                                    value: documento.rne_state,
                                    allowBlank: true,
                                    validateOnBlur: true,
                                    blankText: "",
                                    store: this.getStore("estado"),
                                    displayField: 'description',
                                    typeAhead: true,
                                    mode: "local",
                                    triggerAction: 'all',
                                    emptyText: 'Selecione um item...',
                                    selectOnFocus: true,
                                    editable: true
                                },
                                {
                                    autoWidth: true,
                                    name: "nis",
                                    fieldLabel: "NIS",
                                    xtype: "textfield",
                                    allowBlank: true,
                                    validateOnBlur: true,
                                    blankText: "",
                                    value: documento.nis
                                },
                            ]
                        }]
                    });
                    column2_items.push(f1);

                    f1 = new Ext.Panel({
                        layout: 'column',
                        items: [{
                            columnWidth: ".50",
                            layout: 'form',
                            items: [{
                                autoWidth: true,
                                name: "cnh",
                                fieldLabel: "CNH",
                                xtype: "textfield",
                                allowBlank: true,
                                validateOnBlur: true,
                                blankText: "É necessário preencher este campo.",
                                value: documento.cnh
                            }]
                        },
                        {
                            columnWidth: ".50",
                            layout: 'form',
                            items: [{
                                autoWidth: true,
                                name: "cnh_categoria",
                                fieldLabel: "CNH - Categoria",
                                xtype: "textfield",
                                allowBlank: true,
                                validateOnBlur: true,
                                blankText: "É necessário preencher este campo.",
                                value: documento.cnh_categoria
                            }]
                        }]
                    });
                    column1_items.push(f1);

                    f1 = new Ext.Panel({
                        layout: 'column',
                        items: [{
                            columnWidth: ".50",
                            layout: 'form',
                            items: [{
                                autoWidth: true,
                                name: "cnh_expedition_date",
                                fieldLabel: "CNH - Data Expedição",
                                xtype: "datefield",
                                allowBlank: true,
                                validateOnBlur: true,
                                blankText: "É necessário preencher este campo.",
                                value: documento.cnh_expedition_date
                            }]
                        },
                        {
                            columnWidth: ".50",
                            layout: 'form',
                            items: [{
                                autoWidth: true,
                                name: "cnh_validity_date",
                                fieldLabel: "CNH - Data Validate",
                                xtype: "datefield",
                                allowBlank: true,
                                validateOnBlur: true,
                                blankText: "É necessário preencher este campo.",
                                value: documento.cnh_validity_date
                            }]
                        }]
                    });
                    column1_items.push(f1);

                    f1 = new Ext.Panel({
                        layout: 'column',
                        items: [{
                            columnWidth: ".50",
                            layout: 'form',
                            items: [{
                                autoWidth: true,
                                name: "cnh_first_date",
                                fieldLabel: "CNH - Data Primeira Habilitação",
                                xtype: "datefield",
                                allowBlank: true,
                                validateOnBlur: true,
                                blankText: "É necessário preencher este campo.",
                                value: documento.cnh_first_date
                            }]
                        },
                        {
                            columnWidth: ".50",
                            layout: 'form',
                            items: [{
                                width: 350,
                                hiddenName: "cnh_state",
                                fieldLabel: "CNH - UF",
                                xtype: "combo",
                                value: documento.cnh_state,
                                allowBlank: true,
                                validateOnBlur: true,
                                blankText: "",
                                store: this.getStore("estado"),
                                displayField: 'description',
                                typeAhead: true,
                                mode: "local",
                                triggerAction: 'all',
                                emptyText: 'Selecione um item...',
                                selectOnFocus: true,
                                editable: true
                            }]
                        }]
                    });
                    column1_items.push(f1);

                    f1 = new Ext.Panel({
                        layout: 'column',
                        items: [{
                            columnWidth: ".50",
                            layout: 'form',
                            items: [{
                                autoWidth: true,
                                name: "ctps",
                                fieldLabel: "CTPS",
                                xtype: "textfield",
                                allowBlank: true,
                                validateOnBlur: true,
                                blankText: "É necessário preencher este campo.",
                                value: documento.ctps
                            }]
                        },
                        {
                            columnWidth: ".50",
                            layout: 'form',
                            items: [{
                                autoWidth: true,
                                name: "serie_ctps",
                                fieldLabel: "Série  de CTPS",
                                xtype: "textfield",
                                allowBlank: true,
                                validateOnBlur: true,
                                blankText: "É necessário preencher este campo.",
                                value: documento.serie_ctps
                            }]
                        }]
                    });
                    column1_items.push(f1);

                    f1 = new Ext.Panel({
                        layout: 'column',
                        items: [{
                            columnWidth: ".50",
                            layout: 'form',
                            items: [{
                                width: 350,
                                hiddenName: "ctps_state",
                                fieldLabel: "CTPS - UF",
                                xtype: "combo",
                                value: documento.ctps_state,
                                allowBlank: true,
                                validateOnBlur: true,
                                blankText: "",
                                store: this.getStore("estado"),
                                displayField: 'description',
                                typeAhead: true,
                                mode: "local",
                                triggerAction: 'all',
                                emptyText: 'Selecione um item...',
                                selectOnFocus: true,
                                editable: true
                            }]
                        }]
                    });
                    column1_items.push(f1);

                    column1_items.push({
                        width: "95%",
                        name: "pis_pasep",
                        fieldLabel: "PIS/PASEP",
                        xtype: "numberfield",
                        allowBlank: true,
                        validateOnBlur: true,
                        blankText: "É necessário preencher este campo.",
                        value: documento.pis_pasep
                    });

                    f1 = new Ext.Panel({
                        layout: 'column',
                        items: [{
                            columnWidth: ".50",
                            layout: 'form',
                            items: [{
                                autoWidth: true,
                                name: "reservista",
                                fieldLabel: "Reservista",
                                xtype: "textfield",
                                allowBlank: true,
                                validateOnBlur: true,
                                blankText: "É necessário preencher este campo.",
                                value: documento.reservista
                            }]
                        },
                        {
                            columnWidth: ".50",
                            layout: 'form',
                            items: [{
                                autoWidth: true,
                                name: "classe_reservista",
                                fieldLabel: "Classe de Reservista",
                                xtype: "textfield",
                                allowBlank: true,
                                validateOnBlur: true,
                                blankText: "É necessário preencher este campo.",
                                value: documento.classe_reservista
                            }]
                        }]
                    });
                    column1_items.push(f1);

                    f1 = new Ext.Panel({
                        layout: 'column',
                        items: [{
                            columnWidth: ".50",
                            layout: 'form',
                            items: [{
                                autoCreate: { tag: 'input', maxlength: '30' },
                                width: "95%",
                                name: "professional_council",
                                fieldLabel: "Conselho Profissional - Número",
                                xtype: "textfield",
                                allowBlank: true,
                                validateOnBlur: true,
                                blankText: "É necessário preencher este campo.",
                                value: documento.professional_council
                            }]
                        },
                        {
                            columnWidth: ".50",
                            layout: 'form',
                            items: [{
                                width: 350,
                                hiddenName: "professional_council_state",
                                fieldLabel: "Conselho Profissional - UF",
                                xtype: "combo",
                                value: documento.professional_council_state,
                                allowBlank: true,
                                validateOnBlur: true,
                                blankText: "",
                                store: this.getStore("estado"),
                                displayField: 'description',
                                typeAhead: true,
                                mode: "local",
                                triggerAction: 'all',
                                emptyText: 'Selecione um item...',
                                selectOnFocus: true,
                                editable: true
                            }]
                        }]
                    });
                    column1_items.push(f1);

                    f1 = new Ext.Panel({
                        layout: 'column',
                        items: [{
                            columnWidth: ".50",
                            layout: 'form',
                            items: [{
                                name: "professional_council_expedition_date",
                                fieldLabel: "Conselho Profissional - Data de Expedição",
                                xtype: "datefield",
                                value: documento.professional_council_expedition_date,
                                allowBlank: true,
                                validateOnBlur: true,
                                blankText: ""
                            }]
                        },
                        {
                            columnWidth: ".50",
                            layout: 'form',
                            items: [{
                                name: "professional_council_validity_date",
                                fieldLabel: "Conselho Profissional - Data de Validate",
                                xtype: "datefield",
                                value: documento.professional_council_validity_date,
                                allowBlank: true,
                                validateOnBlur: true,
                                blankText: ""

                            }]
                        }]
                    });
                    column1_items.push(f1);

                    column1_items.push({
                        autoCreate: { tag: 'input', maxlength: '30' },
                        width: "95%",
                        name: "professional_council_issuer",
                        fieldLabel: "Conselho Profissional - Órgão Emissor",
                        xtype: "textfield",
                        allowBlank: true,
                        validateOnBlur: true,
                        blankText: "É necessário preencher este campo.",
                        value: documento.professional_council_issuer
                    });

                    column1_items.push({
                        width: "95%",
                        name: "titulo_eleitor",
                        fieldLabel: "Título de Eleitor",
                        xtype: "textfield",
                        allowBlank: false,
                        validateOnBlur: true,
                        blankText: "É necessário preencher este campo.",
                        value: documento.titulo_eleitor
                    });

                    f1 = new Ext.Panel({
                        layout: 'column',
                        items: [{
                            columnWidth: ".50",
                            layout: 'form',
                            items: [{
                                autoWidth: true,
                                name: "zona_titulo",
                                fieldLabel: "Zona de Título",
                                xtype: "textfield",
                                allowBlank: false,
                                validateOnBlur: true,
                                blankText: "É necessário preencher este campo.",
                                value: documento.zona_titulo
                            }]
                        },
                        {
                            columnWidth: ".50",
                            layout: 'form',
                            items: [{
                                autoWidth: true,
                                name: "secao_titulo",
                                fieldLabel: "Seção de Título",
                                xtype: "textfield",
                                allowBlank: false,
                                validateOnBlur: true,
                                blankText: "É necessário preencher este campo.",
                                value: documento.secao_titulo
                            }]
                        }]
                    });
                    column1_items.push(f1);

                    column1_items.push({
                        width: 350,
                        hiddenName: "municipio_titulo",
                        fieldLabel: "Município de Título",
                        displayField: "description",
                        allowBlank: false,
                        valueField: "pk",
                        conf: { "addLabel": "Criar ...", "editLabel": "Modificar ...", "canAdd": true, "canEdit": true },
                        triggerAction: "all",
                        queryAction: "query",
                        model: "Localidade",
                        hideTrigger: true,
                        queryParam: "keyword",
                        crudController: "RHLocalidade",
                        xtype: "autocompletefield",
                        value: documento.municipio_titulo
                    });
                    column1_items.push({
                        width: 350,
                        hiddenName: "molestia",
                        fieldLabel: "Moléstia",
                        displayField: "description",
                        allowBlank: true,
                        valueField: "pk",
                        conf: { "addLabel": "Criar ...", "editLabel": "Modificar ...", "canAdd": true, "canEdit": true },
                        triggerAction: "all",
                        queryAction: "query",
                        model: "Molestia",
                        hideTrigger: true,
                        queryParam: "keyword",
                        crudController: "RHMolestia",
                        xtype: "autocompletefield",
                        value: pessoa_fisica.molestia
                    });

                    var f = new Ext.Panel({
                        layout: 'column',
                        items: [{
                            columnWidth: ".5",
                            layout: 'form',
                            items: column1_items
                        }, {
                            columnWidth: ".5",
                            layout: 'form',
                            items: column2_items
                        }]
                    });

                    setTimeout(function () { f.doLayout(); }, 250);
                    var column = [f];
                    return column;
                },

                getTabDocumentsGrid: function (cfg) {
                    if (!this._tabDocumentsGrid) {
                        this._tabDocumentsGrid = Ext._create('rh.documento.DocumentoGrid', {
                            title: 'Documentos',
                            hideItemsToolbar: ['search', 'download'],
                            region: 'center',
                            border: false,
                            scope: this,
                            height: 425,
                            gridAutoLoad: false,
                        });
                    }
                    return this._tabDocumentsGrid;
                },

                getTabContacts: function () {
                    if (!this.tabContacts) {
                        this.tabContacts = new Ext.Panel({
                            title: 'Telefones/Endereço',
                            iconCls: 'icon-rh icon-core-contacts-tab',
                            layout: 'border',
                            autoRender: true,
                            border: false,
                            // style: 'margin: 2pt',
                            autoScroll: true,
                            items: [
                                this.getAddressGrid(),
                                this.getPhoneGrid()
                            ],
                            listeners: {
                                scope: this,
                                beforeshow: function (panel) {
                                    try { if (!this.tabContacts.layout_show) this.activePanel.doLayout(); }
                                    catch (e) { console.debug(e); }
                                },
                                afterlayout: function (layout) {
                                    this.tabContacts.layout_show = true;
                                }
                            }
                        });
                        this.tabContacts.layout_show = false;
                    }
                    return this.tabContacts;
                },

                getTabPhone: function () {
                    if (!this.tabPhone) {
                        this.tabPhone = new Ext.Panel({
                            title: 'Telefones',
                            iconCls: 'icon-rh icon-core-contacts-tab',
                            layout: 'border',
                            autoRender: true,
                            border: false,
                            // style: 'margin: 2pt',
                            autoScroll: true,
                            items: [
                                this.getPhoneGrid()
                            ],
                            listeners: {
                                scope: this,
                                beforeshow: function (panel) {
                                    try { if (!this.tabPhone.layout_show) this.activePanel.doLayout(); }
                                    catch (e) { console.debug(e); }
                                },
                                afterlayout: function (layout) {
                                    this.tabPhone.layout_show = true;
                                }
                            }
                        });
                        this.tabPhone.layout_show = false;
                    }
                    return this.tabPhone;
                },

                getPhoneGrid: function (cfg) {
                    if (!this._phoneGrid) {
                        this._phoneGrid = Ext._create('rh.telefone.TelefoneGrid', {
                            hideItemsToolbar: ['search', 'download'],
                            title: 'Telefones',
                            style: 'margin: 2pt',
                            region: 'north',
                            border: false,
                            scope: this,
                            height: 425,
                            columnAction: false,
                            gridAutoLoad: false,
                        });
                    }
                    return this._phoneGrid;
                },

                getTabAddress: function () {
                    if (!this.tabAddress) {
                        this.tabAddress = new Ext.Panel({
                            iconCls: 'icon-rh icon-core-address-tab',
                            title: 'Endereço',
                            layout: 'border',
                            autoRender: true,
                            border: false,
                            // style: 'margin: 2pt',
                            autoScroll: true,
                            items: [
                                this.getAddressGrid()
                            ],
                            listeners: {
                                scope: this,
                                beforeshow: function (panel) {
                                    try { if (!this.tabAddress.layout_show) this.activePanel.doLayout(); }
                                    catch (e) { console.debug(e); }
                                },
                                afterlayout: function (layout) {
                                    this.tabAddress.layout_show = true;
                                }
                            }
                        });
                        this.tabAddress.layout_show = false;
                    }
                    return this.tabAddress;
                },

                getAddressGrid: function (cfg) {
                    if (!this._addressGrid) {
                        this._addressGrid = Ext._create('rh.endereco.EnderecoGrid', {
                            hideItemsToolbar: ['search', 'download'],
                            title: 'Endereço',
                            style: 'margin: 2pt',
                            region: 'center',
                            border: false,
                            scope: this,
                            height: 455,
                            columnAction: false,
                            gridAutoLoad: false,
                        });
                    }
                    return this._addressGrid;
                },

                getTabHealth: function () {
                    if (!this._tabHealth) {
                        this._tabHealth = new Ext.Panel({
                            iconCls: 'icon-rh icon-core-health-tab',
                            title: 'Saúde',
                            layout: 'border',
                            autoRender: true,
                            style: 'margin: 2pt',
                            autoScroll: true,
                            items: [
                                this.getSpecialNeedsField({}),
                                this.getSeriousDiseasesField({}),
                                this.getDeficiencyInformationGrid({})
                            ],
                            listeners: {
                                scope: this,
                                beforeshow: function (panel) {
                                    try { if (!this._tabHealth.layout_show) this.activePanel.doLayout(); }
                                    catch (e) { console.debug(e); }
                                },
                                afterlayout: function (layout) {
                                    this._tabHealth.layout_show = true;
                                }
                            }
                        });
                        this._tabHealth.layout_show = false;
                    }
                    return this._tabHealth;
                },

                getSpecialNeedsField: function (cfg) {
                    if (!this._specialNeedsField)
                        this._specialNeedsField = Ext._create('core.fields.RelatedRestfulField', {
                            title: 'Necessidades especiais',
                            style: 'margin: 2pt',
                            region: 'north',
                            xtype: 'rest-relatedfield',
                            // hideLabel: true,
                            name: 'necessidades_especiais',
                            displayField: 'unicode',
                            allowBlank: false,
                            relatedname: 'pessoa',
                            rest: 'rh.person.naturalperson.Restful',
                            sourceRest: 'rh.necessidadeespecial.Restful',
                            oId: this.getPerson(),
                            // width: 535,
                            minHeight: 150,
                            height: 175,
                            border: false
                        });

                    return this._specialNeedsField;
                },

                getSeriousDiseasesField: function (cfg) {
                    if (!this._seriousDiseasesField)
                        this._seriousDiseasesField = Ext._create('core.fields.RelatedRestfulField', {
                            style: 'margin: 2pt',
                            region: 'center',
                            xtype: 'rest-relatedfield',
                            title: 'Doenças Graves',
                            // hideLabel: true,
                            name: 'serious_diseases',
                            displayField: 'name',
                            allowBlank: false,
                            relatedname: 'in_pessoafisica',
                            rest: 'rh.person.naturalperson.Restful',
                            sourceRest: 'rh.seriousdiseases.Restful',
                            oId: this.getPerson(),
                            // width: 535,
                            minHeight: 150,
                            height: 175,
                            border: false
                        });

                    return this._seriousDiseasesField;
                },

                getDeficiencyInformationGrid: function (cfg) {
                    if (!this._deficiencyInformationGrid)
                        this._deficiencyInformationGrid = Ext._create('rh.deficiencyinformation.Grid', {
                            style: 'margin: 2pt',
                            title: 'Informações complementares de deficiência',
                            hideItemsToolbar: ['search', 'download'],
                            region: 'south',
                            border: false,
                            scope: this,
                            minHeight: 150,
                            height: 175,
                            columnAction: false,
                        });
                    return this._deficiencyInformationGrid;
                },

                getTabDadosFuncionais: function () {
                    if (!this.tabDadosFuncionais) {
                        this.tabDadosFuncionais = new Ext.Panel({
                            title: "Dados Funcionais",
                            layout: 'border',
                            autoRender: true,
                            border: false,
                            style: 'margin: 2pt',
                            autoScroll: true,
                            items: [
                                this.getDadosFuncionaisFields(),
                                this.getDadosFuncionaisEstaticosFields()
                            ],
                            listeners: {
                                scope: this,
                                beforeshow: function (panel) {
                                    try { if (!this.tabDadosFuncionais.layout_show) this.activePanel.doLayout(); }
                                    catch (e) { console.debug(e); }
                                },
                                afterlayout: function (layout) {
                                    this.tabDadosFuncionais.layout_show = true;
                                }
                            }
                        });
                        this.tabDadosFuncionais.layout_show = false;
                    }
                    return this.tabDadosFuncionais;
                },

                getDegreeEducationChoiceField: function (cfg) {
                    if (!this._degreeEducationChoiceField) {
                        cfg = cfg || {};
                        Ext.applyIf(cfg, {
                            fieldLabel: 'Grau Instrução',
                            hiddenName: 'grau_instrucao',
                            choiceId: 'rh.DEGREE_EDUCATION',
                            width: 350
                        });
                        this._degreeEducationChoiceField = Ext._create('standard.fields.ChoiceField', cfg);
                        var store = this._degreeEducationChoiceField.getStore();
                        var filter = Ext.decode(store.baseParams.filter);
                        filter.push({ property: 'value__in', value: [3, 12, 13, 14], stage: -1 });
                        store.baseParams.filter = Ext.encode(filter);
                        store.load();
                    }
                    return this._degreeEducationChoiceField;
                },

                getDadosFuncionaisFields: function () {
                    var column1_items = [];
                    var column2_items = [];
                    servidor = this.store_data_servidor.servidor;
                    column1_items.push({
                        width: "95%",
                        name: "matricula",
                        fieldLabel: "Matrícula",
                        xtype: "textfield",
                        allowBlank: false,
                        validateOnBlur: true,
                        blankText: "É necessário preencher este campo.",
                        value: servidor.matricula
                    });
                    column1_items.push({
                        name: "data_referencia_ferias",
                        fieldLabel: "Data referência férias",
                        xtype: "datefield",
                        value: servidor.data_referencia_ferias,
                        allowBlank: true,
                        validateOnBlur: true,
                        blankText: "É necessário preencher este campo."
                    });
                    column1_items.push({
                        width: 100,
                        hiddenName: "regime_previdenciario",
                        fieldLabel: "Regime Previdenciário",
                        xtype: "combo",
                        value: servidor.regime_previdenciario ? servidor.regime_previdenciario : 2,
                        allowBlank: true,
                        validateOnBlur: true,
                        blankText: "É necessário preencher este campo.",
                        store: rh.employee.specialized.CHOICES.REGIME_PREVIDENCIARIO,
                        displayField: 'description',
                        typeAhead: true,
                        mode: "local",
                        triggerAction: 'all',
                        emptyText: 'Selecione um item...',
                        selectOnFocus: true,
                        editable: true
                    });
                    column1_items.push({
                        width: 300,
                        hiddenName: "chefe_imediato",
                        fieldLabel: "Chefe imediato",
                        displayField: "description",
                        allowBlank: true,
                        valueField: "pk",
                        conf: { "addLabel": "Criar ...", "editLabel": "Modificar ...", "canAdd": false, "canEdit": false },
                        triggerAction: "all",
                        queryAction: "query",
                        model: "Servidor",
                        hideTrigger: true,
                        queryParam: "keyword",
                        crudController: "RHServidor",
                        xtype: "autocompletefield",
                        value: servidor.chefe_imediato
                    });
                    column1_items.push({
                        width: 300,
                        hiddenName: "organ_social_security",
                        fieldLabel: "Órgão previdenciário",
                        displayField: "description",
                        allowBlank: true,
                        valueField: "pk",
                        conf: { "addLabel": "Criar ...", "editLabel": "Modificar ...", "canAdd": false, "canEdit": false },
                        triggerAction: "all",
                        queryAction: "query",
                        model: "PessoaJuridica",
                        hideTrigger: true,
                        queryParam: "keyword",
                        crudController: "RHPessoaJuridica",
                        xtype: "autocompletefield",
                        value: servidor.organ_social_security
                    });
                    column2_items.push({
                        width: "95%",
                        name: "matricula_origem",
                        fieldLabel: "Matrícula de Origem",
                        xtype: "textfield",
                        allowBlank: true,
                        validateOnBlur: true,
                        blankText: "É necessário preencher este campo.",
                        value: servidor.matricula_origem
                    });
                    column2_items.push({
                        width: "95%",
                        name: "numero_cartao_ponto",
                        fieldLabel: "N° Cartão de Ponto",
                        xtype: "numberfield",
                        allowBlank: true,
                        validateOnBlur: true,
                        blankText: "É necessário preencher este campo.",
                        value: servidor.numero_cartao_ponto
                    });
                    column2_items.push(
                        this.getDegreeEducationChoiceField({ value: servidor.grau_instrucao ? servidor.grau_instrucao : 8 })
                    );

                    var c = new Ext.Panel({
                        region: 'north',
                        height: 250,
                        layout: 'column',
                        items: [{
                            columnWidth: ".5",
                            layout: 'form',
                            items: column1_items
                        },
                        {
                            columnWidth: ".5",
                            layout: 'form',
                            items: column2_items
                        }]
                    });

                    setTimeout(function () { c.doLayout(); }, 250);
                    var column = [c];
                    return column;
                },

                getDadosFuncionaisEstaticosFields: function () {
                    return new Ext.Panel({
                        region: 'center',
                        autoRender: true,
                        autoScroll: true,
                        style: 'margin: 2pt',
                        items: [
                            new toolkit.rh.servidor.utils.InformacoesFieldSet(
                                this.store_data_servidor.dados_estaticos_informacoes),
                            new toolkit.rh.servidor.utils.EfetivoFieldSet(
                                this.store_data_servidor.dados_estaticos_efetivo),
                            new toolkit.rh.servidor.utils.ComissaoFieldSet(
                                this.store_data_servidor.dados_estaticos_cmfc),
                            new toolkit.rh.servidor.utils.EletivoFieldSet(
                                this.store_data_servidor.dados_estaticos_eletivo),
                            (new toolkit.rh.servidor.utils.DesignacaoFieldSet({
                                titulo: "Designação",
                                store_name: "designacao",
                                servidor: this.getEmployee(),
                                father: this,
                                controller: "RHServidorLotacao"
                            })).getFieldSet()
                        ]
                    });
                },

                getTabOutrasInformacoes: function () {
                    if (!this.tabOutrasInformacoes) {
                        this.tabOutrasInformacoes = new Ext.Panel({
                            title: "Outras Informações",
                            autoRender: true,
                            border: false,
                            style: 'margin: 2pt',
                            autoScroll: true,
                            items: this.getTabOutrasInformacoesFields(),
                            listeners: {
                                scope: this,
                                beforeshow: function (panel) {
                                    try { if (!this.tabOutrasInformacoes.layout_show) this.activePanel.doLayout(); }
                                    catch (e) { console.debug(e); }
                                },
                                afterlayout: function (layout) { this.tabOutrasInformacoes.layout_show = true; }
                            }
                        });
                        this.tabOutrasInformacoes.layout_show = false;
                    }
                    return this.tabOutrasInformacoes;
                },

                getDigitalDocumentsGrid: function () {
                    return undefined;
                },

                getTabOutrasInformacoesFields: function () {
                    var column1_items = [];
                    var column2_items = [];
                    servidor = this.store_data_servidor.servidor;

                    var gridDigitalDocuments = this.getDigitalDocumentsGrid();

                    var digitalDocuments = {
                        xtype: 'fieldset',
                        collapsible: true,
                        title: 'Documentos Digitais',
                        height: 400,
                        autoWidth: true,
                        collapsed: false,
                        items: [gridDigitalDocuments]
                    };
                    column1_items.push(digitalDocuments);
                    column1_items.push({
                        width: "95%",
                        title: "Curso",
                        name: "curso",
                        frame: true,
                        xtype: "multiselectbox",
                        allowBlank: true,
                        validateOnBlur: true,
                        blankText: "É necessário preencher este campo.",
                        model: { name: "Curso", pkg: "rh.models" },
                        controller: "RHCurso",
                        queryset: [],
                        value: servidor.curso
                    });

                    var panel = new Ext.Panel({
                        items: column1_items
                    });
                    setTimeout(function () { panel.doLayout(); }, 250);
                    return panel;
                },

                getTabMovimentacoes: function () {
                    if (!this.tabMovimentacoes) {
                        this.tabMovimentacoes = new Ext.Panel({
                            title: "Movimentações",
                            border: false,
                            autoRender: true,
                            autoScroll: true,
                            autoWidth: true,
                            items: new Ext.Panel({ items: this.getTabMovimentacoesFields() }),
                            listeners: {
                                scope: this,
                                beforeshow: function (panel) {
                                    try { if (!this.tabMovimentacoes.layout_show) this.activePanel.doLayout(); }
                                    catch (e) { console.debug(e); }
                                },
                                afterlayout: function (layout) { this.tabMovimentacoes.layout_show = true; }
                            }
                        });
                        this.tabMovimentacoes.layout_show = false;
                    }
                    return this.tabMovimentacoes;
                },

                getTabMovimentacoesFields: function () {
                    var items = [];

                    this._workplaceGrid = this._factoryGrid('rh.employee.workplace.managerbyemployee.WorkplaceGrid', {}, this.getEmployee());
                    this._workassignmentGrid = this._factoryGrid('rh.employee.workplace.managerbyemployee.WorkassignmentGrid', {}, this.getEmployee());
                    this._concession = this._factoryGrid('rh.movimentacao.concession.Grid', {}, this.getEmployee());
                    this._progression = this._factoryGrid('rh.movimentacao.progression.Grid', {}, this.getEmployee());
                    this._legalframing = this._factoryGrid('rh.movimentacao.progression.legalframing.Grid', {}, this.getEmployee());
                    this._redistribution = this._factoryGrid('rh.movimentacao.redistribution.Grid', {}, this.getEmployee());
                    this._requisition = this._factoryGrid('rh.movimentacao.requisicao.Grid', {}, this.getEmployee());
                    this._removal = this._factoryGrid('rh.movimentacao.removal.Grid', {}, this.getEmployee());
                    this._diligence = this._factoryGrid('rh.movimentacao.diligence.Grid', this.getEmployee());
                    this._aux_coordenation = this._factoryGrid('rh.movimentacao.aux_coordenation.Grid', this.getEmployee());
                    this._teletrabalho = this._factoryGrid('rh.movimentacao.teletrabalho.Grid', this.getEmployee());

                    items = [
                        this._factoryFieldSet({ title: 'Lotação', items: [this._workplaceGrid], height: 350 }, this._workplaceGrid),
                        this._factoryFieldSet({ title: 'Exercício', items: [this._workassignmentGrid], height: 350 }, this._workassignmentGrid),
                        this._factoryFieldSet({ title: 'Concessão', items: [this._concession] }, this._concession),
                        this._factoryFieldSet({ title: 'Progressão', items: [this._progression] }, this._progression),
                        this._factoryFieldSet({ title: 'Enquadramento', items: [this._legalframing] }, this._legalframing),
                        this._factoryFieldSet({ title: 'Redistribuição', items: [this._redistribution] }, this._redistribution),
                        this._factoryFieldSet({ title: 'Requisição', items: [this._requisition] }, this._requisition),
                        this._factoryFieldSet({ title: 'Remoção', items: [this._removal] }, this._removal),
                        this._factoryFieldSet({ title: 'Designação para Diligência', items: [this._diligence] }, this._diligence),
                        this._factoryFieldSet({ title: 'Teletrabalho', items: [this._teletrabalho] }, this._teletrabalho),
                    ];
                    return items;
                },

                getProvisionGrid: function () {
                    if (this.abaProvimentos == undefined) {
                        console.debug('criando....');
                        this.abaProvimentos = Ext._create('rh.movimentacao.possession.provision.Grid', { title: 'Provimentos', gridAutoLoad: false });
                        this.abaProvimentos.setFilterProperty('servidor__id', this.getEmployee());
                        this.abaProvimentos.setParam('servidor', this.getEmployee());
                    } else
                        console.debug('utilizando....');
                    console.debug(this.abaProvimentos);
                    return this.abaProvimentos;
                },

                getTabAnotacoes: function () {
                    if (!this.tabAnotacoes) {
                        this.tabAnotacoes = new Ext.Panel({
                            title: "Anotações",
                            border: false,
                            autoRender: true,
                            autoScroll: true,
                            autoWidth: true,
                            items: new Ext.Panel({ items: this.getTabAnotacoesFields() }),
                            listeners: {
                                scope: this,
                                beforeshow: function (panel) {
                                    try {
                                        if (!this.tabAnotacoes.layout_show) {
                                            this.activePanel.doLayout();
                                        }
                                    }
                                    catch (e) { console.debug(e); }
                                },
                                afterlayout: function (layout) { this.tabAnotacoes.layout_show = true; }
                            }
                        });
                        this.tabAnotacoes.layout_show = false;
                    }
                    return this.tabAnotacoes;
                },

                getTabAnotacoesFields: function () {
                    var items = [];
                    this._anotacaoafastamento = this._factoryGrid('rh.anotacao.anotacaoafastamento.Grid', {}, this.getEmployee());
                    this._anotacaoausencia = this._factoryGrid('rh.anotacao.anotacaoausencia.Grid', {}, this.getEmployee());
                    this._anotacaocomunicacao = this._factoryGrid('rh.anotacao.anotacaocomunicacao.Grid', {}, this.getEmployee());
                    this._anotacaoelogio = this._factoryGrid('rh.anotacao.anotacaoelogio.Grid', {}, this.getEmployee());
                    this._anotacaocarreira = this._factoryGrid('rh.anotacao.anotacaocarreira.Grid', {}, this.getEmployee());
                    this._anotacaoevento = this._factoryGrid('rh.anotacao.anotacaoevento.Grid', {}, this.getEmployee());
                    this._anotacaofalta = this._factoryGrid('rh.anotacao.anotacaofalta.Grid', {}, this.getEmployee());
                    this._anotacaoferias = this._factoryGrid('rh.anotacao.anotacaoferias.Grid', {}, this.getEmployee());
                    this._anotacaofolgaaniversario = this._factoryGrid('rh.anotacao.anotacaofolgaaniversario.Grid', {}, this.getEmployee());
                    this._anotacaofolgacompensacao = this._factoryGrid('rh.anotacao.anotacaofolgacompensacao.Grid', {}, this.getEmployee());
                    this._anotacaofolgaeleitoral = this._factoryGrid('rh.anotacao.anotacaofolgaeleitoral.Grid', {}, this.getEmployee());
                    this._anotacaobancodehoras = this._factoryGrid('rh.anotacao.anotacaobancodehoras.Grid', {}, this.getEmployee());
                    this._anotacaogeral = this._factoryGrid('rh.anotacao.anotacaogeral.Grid', {}, this.getEmployee());
                    this._anotacaogratificacao = this._factoryGrid('rh.anotacao.anotacaogratificacao.Grid', {}, this.getEmployee());
                    this._anotacaohorarioespecial = this._factoryGrid('rh.anotacao.anotacaohorarioespecial.Grid', {}, this.getEmployee());
                    this._anotacaolicenca = this._factoryGrid('rh.anotacao.anotacaolicenca.Grid', {}, this.getEmployee());
                    this._anotacaopenadisciplinar = this._factoryGrid('rh.anotacao.anotacaopenadisciplinar.Grid', {}, this.getEmployee());
                    this._anotacaorecesso = this._factoryGrid('rh.anotacao.anotacaorecesso.Grid', {}, this.getEmployee());
                    this._anotacaoremocao = this._factoryGrid('rh.anotacao.anotacaoremocao.Grid', {}, this.getEmployee());
                    this._anotacaotempodobro = this._factoryGrid('rh.anotacao.anotacaotempodobro.Grid', {}, this.getEmployee());
                    this._anotacaotemposervico = this._factoryGrid('rh.anotacao.anotacaotemposervico.Grid', {}, this.getEmployee());
                    this._anotacaotransposicao = this._factoryGrid('rh.anotacao.anotacaotransposicao.Grid', {}, this.getEmployee());

                    items = [
                        this._factoryFieldSet({ title: 'Anotação Afastamento', items: [this._anotacaoafastamento] }, this._anotacaoafastamento),
                        this._factoryFieldSet({ title: 'Anotação Ausência', items: [this._anotacaoausencia] }, this._anotacaoausencia),
                        this._factoryFieldSet({ title: 'Anotação Comunicação', items: [this._anotacaocomunicacao] }, this._anotacaocomunicacao),
                        this._factoryFieldSet({ title: 'Anotação Elogio', items: [this._anotacaoelogio] }, this._anotacaoelogio),
                        this._factoryFieldSet({ title: 'Anotação Carreira', items: [this._anotacaocarreira] }, this._anotacaocarreira),
                        this._factoryFieldSet({ title: 'Anotação Evento', items: [this._anotacaoevento] }, this._anotacaoevento),
                        this._factoryFieldSet({ title: 'Anotação Falta', items: [this._anotacaofalta] }, this._anotacaofalta),
                        this._factoryFieldSet({ title: 'Anotação Férias', items: [this._anotacaoferias] }, this._anotacaoferias),
                        this._factoryFieldSet({ title: 'Anotação Folga Aniversário', items: [this._anotacaofolgaaniversario] }, this._anotacaofolgaaniversario),
                        this._factoryFieldSet({ title: 'Anotação Folga Compensação', items: [this._anotacaofolgacompensacao] }, this._anotacaofolgacompensacao),
                        this._factoryFieldSet({ title: 'Anotação Folga Eleitoral', items: [this._anotacaofolgaeleitoral] }, this._anotacaofolgaeleitoral),
                        this._factoryFieldSet({ title: 'Anotação Banco de Horas', items: [this._anotacaobancodehoras] }, this._anotacaobancodehoras),
                        this._factoryFieldSet({ title: 'Anotação Geral', items: [this._anotacaogeral] }, this._anotacaogeral),
                        this._factoryFieldSet({ title: 'Anotação Gratificação', items: [this._anotacaogratificacao] }, this._anotacaogratificacao),
                        this._factoryFieldSet({ title: 'Anotação Horário Especial', items: [this._anotacaohorarioespecial] }, this._anotacaohorarioespecial),
                        this._factoryFieldSet({ title: 'Anotação Licença', items: [this._anotacaolicenca] }, this._anotacaolicenca),
                        this._factoryFieldSet({ title: 'Anotação Pena Disciplinar', items: [this._anotacaopenadisciplinar] }, this._anotacaopenadisciplinar),
                        this._factoryFieldSet({ title: 'Anotação Recesso', items: [this._anotacaorecesso] }, this._anotacaorecesso),
                        this._factoryFieldSet({ title: 'Anotação Remoção', items: [this._anotacaoremocao] }, this._anotacaoremocao),
                        this._factoryFieldSet({ title: 'Anotação Tempo Dobro', items: [this._anotacaotempodobro] }, this._anotacaotempodobro),
                        this._factoryFieldSet({ title: 'Anotação Tempo Serviço/Contribuição', items: [this._anotacaotemposervico] }, this._anotacaotemposervico),
                        this._factoryFieldSet({ title: 'Anotação Transposição', items: [this._anotacaotransposicao] }, this._anotacaotransposicao),
                    ];
                    return items;
                },

                getTabFormacao: function () {
                    var membro = this.store_data_servidor.servidor.tipo == "M" ? false : true;
                    if (!this.tabFormacao) {
                        this.tabFormacao = new Ext.Panel({
                            title: "Formação",
                            autoRender: true,
                            border: false,
                            disabled: membro,
                            style: 'margin: 2pt',
                            autoScroll: true,
                            items: this.getTabFormacaoFields(),
                            listeners: {
                                scope: this,
                                beforeshow: function (panel) {
                                    try { if (!this.tabFormacao.layout_show) this.activePanel.doLayout(); }
                                    catch (e) { console.debug(e); }
                                },
                                afterlayout: function (layout) { this.tabFormacao.layout_show = true; }
                            }
                        });
                        this.tabFormacao.layout_show = false;
                    }
                    return this.tabFormacao;
                },

                getTabFormacaoFields: function () {
                    var column1_items = [];
                    var column2_items = [];

                    var gridGraduationCNMP = new rh.cnmp.GraduationCNMPGrid({
                        height: 200,
                    });

                    if (this.getEmployee()) {
                        gridGraduationCNMP.setFilterProperty('employee__id', this.getEmployee(), 1001);
                        gridGraduationCNMP.setParam('employee', this.getEmployee());
                        gridGraduationCNMP.enable();
                    }
                    else {
                        gridGraduationCNMP.disable();
                    }

                    var GraduationCNMP = {
                        xtype: 'fieldset',
                        collapsible: true,
                        title: 'Graduação',
                        height: 240,
                        autoWidth: true,
                        collapsed: true,
                        items: [gridGraduationCNMP]
                    };
                    column1_items.push(GraduationCNMP);


                    var gridImprovementAndGraduateCNMP = new rh.cnmp.ImprovementAndGraduateCNMPGrid({
                        height: 200,
                    });

                    if (this.getEmployee()) {
                        gridImprovementAndGraduateCNMP.setFilterProperty('employee__id', this.getEmployee(), 1001);
                        gridImprovementAndGraduateCNMP.setParam('employee', this.getEmployee());
                        gridImprovementAndGraduateCNMP.enable();
                    }
                    else {
                        gridImprovementAndGraduateCNMP.disable();
                    }

                    var ImprovementAndGraduateCNMP = {
                        xtype: 'fieldset',
                        collapsible: true,
                        title: 'Aperfeiçoamento e Pós-Graduação',
                        height: 240,
                        autoWidth: true,
                        collapsed: true,
                        items: [gridImprovementAndGraduateCNMP]
                    };
                    column1_items.push(ImprovementAndGraduateCNMP);


                    var gridPublishedWorksCNMP = new rh.cnmp.PublishedWorksCNMPGrid({
                        height: 200,
                    });

                    if (this.getEmployee()) {
                        gridPublishedWorksCNMP.setFilterProperty('employee__id', this.getEmployee(), 1001);
                        gridPublishedWorksCNMP.setParam('employee', this.getEmployee());
                        gridPublishedWorksCNMP.enable();
                    }
                    else {
                        gridPublishedWorksCNMP.disable();
                    }

                    var PublishedWorksCNMP = {
                        xtype: 'fieldset',
                        collapsible: true,
                        title: 'Trabalhos Publicados',
                        height: 240,
                        autoWidth: true,
                        collapsed: true,
                        items: [gridPublishedWorksCNMP]
                    };
                    column1_items.push(PublishedWorksCNMP);

                    var panel = new Ext.Panel({
                        items: column1_items
                    });
                    setTimeout(function () { panel.doLayout(); }, 250);
                    return panel;
                },
            }),
    });
