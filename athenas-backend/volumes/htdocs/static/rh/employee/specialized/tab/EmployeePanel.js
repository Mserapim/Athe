Ext._define('rh.employee.specialized.tab.EmployeePanel', {
    extend: 'rh.employee.specialized.tab.BaseFormPanel',

    rest: 'rh.employee.specialized.Restful',

    mixins: { '1': 'core.RestfulPanel' },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        var managerTab = cfg.managerTab || -1;
        var employeePk = cfg.employeePk || -1;
        var employeeRegistry = cfg.employeeRegistry || -1;
        var naturalPersonPk = cfg.naturalPersonPk || -1;
        var organIdentifier = cfg.organIdentifier || '';
        var matriculaFieldBlocked = cfg.matriculaFieldBlocked || false;
        var is_member = cfg.is_member || false;

        Ext.applyIf(
            cfg,
            {
                scope: this,
                items: [
                    this.getFormPanel(
                        cfg,
                        {
                            managerTab: managerTab,
                            employeePk: employeePk,
                            employeeRegistry: employeeRegistry,
                            naturalPersonPk: naturalPersonPk,
                            organIdentifier: organIdentifier,
                            matriculaFieldBlocked: matriculaFieldBlocked,
                            is_member: is_member
                        }
                    )
                ],
                buttons: this.getButtons(),
            }
        );
        rh.employee.specialized.tab.EmployeePanel.superclass.constructor.call(this, cfg);

        this._employeePk = employeePk;
        this.cpfExists((naturalPersonPk != undefined && naturalPersonPk != -1) ? true : false);
        this._changePermField(this.cpfExists());

        this.setTabsDisabled(true);
        this._activeTabForm();
        this.mayChangeTabNaturalPersonData(true);
    },

    cpfExists: function (value) {
        if (value != undefined)
            this._cpfExists = value;
        return this._cpfExists;
    },

    _changePermField: function (perm) {
        var items = this.getFormPanel().getForm().items;
        var i = 0;

        for (i = 0; i < items.length; i += 1) {
            var item = items.get(i);
            if (item.name != 'cpf') {
                if (perm == false)
                    item.disable();
                else if (perm == true)
                    item.enable();
            }
        }
    },

    _setNaturalPersonData: function (values) {
        var form = this.getFormPanel().getForm();
        for (var key in values) {
            var field = form.findField(key);
            if (field) {
                if (field.name == 'cpf') {
                    field._preventCallBackReadNaturalPerson = true;
                    field.setValue(values[key]);
                    field._preventCallBackReadNaturalPerson = false;
                } else {
                    field.setValue(values[key]);
                }

                if (field.name == 'foto') {
                    this.getNaturalPersonDataFormPanel().getObjField().getFotoField().setValue(values[key]);
                    // this.getNaturalPersonDataFormPanel().getObjField().getFotoField().observeFileUploaded({file_id: values['foto']});
                }
            }
        }
        this._changePermField(true);
    },

    _readNaturalPersonData: function (cpf) {
        if (!this.cpfExists()) {

            var mask = new Ext.LoadMask(this.getManagerTab().getEl(), { msg: 'Carregando informações do CPF: ' + cpf });
            mask.show();

            Ext.Ajax.request({
                scope: this,
                url: core.callAction('RHNaturalPersonWithDocument', 'v1'),
                params: {
                    filter: Ext.encode([{ 'stage': '0', 'property': 'cpf', 'value': cpf }]),
                },
                method: 'GET',
                callback: function () {
                    mask.hide();
                },
                success: function (xhr) {
                    var rst = Ext.decode(xhr.responseText);
                    this._setNaturalPersonData(rst.collection[0]);
                },
                failure: function (xhr) {
                    Ext.Msg.show({
                        title: 'Informando',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Não foi possível buscar informações para o CPF informado.'
                    });
                }
            });
        }
    },

    _prepareSuccessCallback: function (callback) {
        var wnd = this;
        callback = core.nullValue(callback, {});
        var failure = core.nullValue(callback.failure, {});
        callback = core.nullValue(callback, {});

        callback.success = {
            scope: this,
            fn: function (args) {
                var action = 'create';
                if (args.employeePk)
                    action = 'update';
                this.callReadData(args.employeePk, action);
            }
        };

        callback.failure = {
            scope: this,
            fn: function (args) {
                core.invokeCallback(
                    (failure || { fn: Ext.emptyFn }),
                    args
                );

                if (args.errors) {
                    var me = this;
                    var msgErrors = '';
                    args.errors.forEach(
                        function (error) {
                            var field = me.getFormPanel().getForm().findField(error.field);
                            if (field) {
                                if ((field.name == "naturalPersonPk") || (field.name == "employeePk") || (field.name == "matricula")) {
                                    if (error.values[0] != "None")
                                        me.getFormPanel().getForm().findField(field.name).setValue(error.values[0]);
                                } else {
                                    var tpl = new Ext.XTemplate(
                                        '<ul>',
                                        '<tpl for="values">',
                                        '<li>{.}</li>',
                                        '</tpl>',
                                        '</ul>'
                                    );

                                    field.markInvalid(tpl.apply(error));

                                    error.values.forEach(
                                        function (err) {
                                            msgErrors += err + '\n';
                                        }
                                    );
                                }
                            }
                        }
                    );
                    if (msgErrors != '')
                        alert(msgErrors);
                }
            }
        };
        return callback;
    },

    _activeTabForm: function () {
        var owner = this;
        setTimeout(function () {
            var tabPanel = owner.getItemsFormPanel();
            var activeTab = tabPanel.getActiveTab();
            tabPanel.setActiveTab(owner.getFunctionalDataFormPanel());
            tabPanel.setActiveTab(activeTab);
        }, 500);
    },

    _save: function () {
        this.save(true);
    },

    mayChangeTabNaturalPersonData: function (value) {
        if (value !== undefined)
            this._mayChangeTabNaturalPersonData = value;
        return this._mayChangeTabNaturalPersonData;
    },

    changeActiveTabNaturalPersonData: function () {
        var owner = this;
        setTimeout(function () {
            var tabPanel = owner.getItemsFormPanel();
            var tab = owner.getNaturalPersonDataFormPanel();
            tab.doLayout();
            tabPanel.setActiveTab(tab);
        }, 100);
    },

    readDataCallback: function (instance) {
        this.updateEmployee(instance, this.action);
    },

    callReadData: function (oId, action) {
        this.oId = oId || undefined;
        this.action = action || 'create';
        this.readData();
    },

    setTabsDisabled: function (disabled) {
        if (this.getDocumentPanel()) {
            this.getDocumentPanel().setDisabled(disabled);
        }
        if (this.getDigitalDocumentPanel()) {
            this.getDigitalDocumentPanel().setDisabled(disabled);
        }
        if (this.getNomeacaoPanel()) {
            this.getNomeacaoPanel().setDisabled(disabled);
        }
        if (this.getAdministrativeDocumentPanel()) {
            this.getAdministrativeDocumentPanel().setDisabled(disabled);
        }
        if (this.getContactPanel()) {
            this.getContactPanel().setDisabled(disabled);
        }
        if (this.getHealthPanel()) {
            this.getHealthPanel().setDisabled(disabled);
        }
        if (this.getAnotherInformationPanel()) {
            this.getAnotherInformationPanel().setDisabled(disabled);
        }
        if (this.getDependentPanel()) {
            this.getDependentPanel().setDisabled(disabled);
        }
        if (this.getMovePanel()) {
            this.getMovePanel().setDisabled(disabled);
        }
        if (this.getProvisionPanel()) {
            this.getProvisionPanel().setDisabled(disabled);
        }
        if (this.getAnnotationPanel()) {
            this.getAnnotationPanel().setDisabled(disabled);
        }
        if (this.getGraduationPanel()) {
            this.getGraduationPanel().setDisabled(disabled);
        }
        if (this.getResumePanel()) {
            this.getResumePanel().setDisabled(disabled);
        }
        
    },

    updateEmployee: function (instance, action) {
        instance = instance || {};
        this.oId = instance.pk;
        this.action = action || 'create';

        if (this.oId == undefined)
            this.resetForm();

        var params = {
            managerTab: this.getManagerTab(),
            employeePk: -1,
            employeeRegistry: -1,
            naturalPersonPk: -1,
            is_member: false,
        };
        var employeeTitle = '----';
        var disabled = true;
        if (this.oId != undefined && instance.pk != undefined) {
            Ext.apply(params, {
                employeePk: instance.pk,
                employeeRegistry: instance.matricula,
                naturalPersonPk: instance.naturalPersonPk,
                is_member: instance.is_member
            });
            employeeTitle = instance.matricula + ' | ' + instance.nome;
            employeeTitle = employeeTitle + ' | ' + instance.employee_status;
            employeeTitle = employeeTitle + ' | ' + instance.type_by_possession_display;
            employeeTitle = employeeTitle + ' | ' + instance.situation_functional_information;
            employeeTitle = employeeTitle.toUpperCase();
            this._employeePk = instance.pk;
            disabled = false;
        }
        this.setTabsDisabled(disabled);
        if (this.getNaturalPersonDataFormPanel())
            this.getNaturalPersonDataFormPanel().observe(params);

        if (this.getFunctionalDataFormPanel()){
            this.getFunctionalDataFormPanel().observe(params);}

        if (this.getDocumentPanel()) {
            this.getDocumentPanel().observe(params);
        }
        if (this.getDigitalDocumentPanel()) {
            this.getDigitalDocumentPanel().observe(params);
        }
        if (this.getNomeacaoPanel()) {
            this.getNomeacaoPanel().observe(params);
        }
        if (this.getAdministrativeDocumentPanel()) {
            this.getAdministrativeDocumentPanel().observe(params);
        }
        if (this.getContactPanel()) {
            this.getContactPanel().observe(params);
        }
        if (this.getHealthPanel()) {
            this.getHealthPanel().observe(params);
        }
        if (this.getAnotherInformationPanel()) {
            this.getAnotherInformationPanel().observe(params);
        }
        if (this.getDependentPanel()) {
            this.getDependentPanel().observe(params);
        }
        if (this.getMovePanel()) {
            this.getMovePanel().observe(params);
        }
        if (this.getProvisionPanel()) {
            this.getProvisionPanel().observe(params);
        }
        if (this.getAnnotationPanel()) {
            this.getAnnotationPanel().observe(params);
        }
        if (this.getGraduationPanel()) {
            this.getGraduationPanel().observe(params);
        }
        if (this.getResumePanel()){
            this.getResumePanel().observe(params)
        }
        if (this.getDisplayName()) {
            this.getDisplayName().setValue(employeeTitle);
        }

        if (this.mayChangeTabNaturalPersonData()) {
            var mask = new Ext.LoadMask(this.getManagerTab().getEl(), { msg: 'Carregando informações...' });
            mask.show();
            this.changeActiveTabNaturalPersonData();
            setTimeout(function () {
                mask.hide();
            }, 1000);
        } else
            this.mayChangeTabNaturalPersonData(true);
        this.cpfExists(instance.naturalPersonPk != undefined ? true : false);
        this._changePermField(this.cpfExists());
        if (instance.foto == undefined) {
            this.getNaturalPersonDataFormPanel().getObjField().getFotoField().ownerCt.body.dom.style.background = '';
        }
    },

    getFormPanel: function (cfgPanel, cfg) {
        cfg = core.nullValue(cfg, {});
        if (!this._formPanel) {
            Ext.applyIf(
                cfg,
                {
                    border: false,
                    scope: this,
                    items: [
                        this.getEmployeeNamePanel(),
                        this.getItemsFormPanel(
                            cfgPanel,
                            {
                                managerTab: cfg.managerTab,
                                employeePk: cfg.employeePk,
                                employeeRegistry: cfg.employeeRegistry,
                                naturalPersonPk: cfg.naturalPersonPk,
                                organIdentifier: cfg.organIdentifier,
                                matriculaFieldBlocked: cfg.matriculaFieldBlocked,
                                is_member: cfg.is_member
                            }
                        ),
                    ]
                }
            );
            this._formPanel = Ext._create('Ext.form.FormPanel', cfg);
        }
        return this._formPanel;
    },

    getEmployeeNamePanel: function () {
        if (!this._employeeNamePanel) {
            this._employeeNamePanel = Ext._create('Ext.Panel', {
                border: false,
                items: [
                    this.getDisplayName()
                ]
            });
        }
        return this._employeeNamePanel;
    },

    getDisplayName: function () {
        if (!this._displayName) {
            this._displayName = Ext._create('Ext.form.DisplayField', {
                style: 'padding: 4pt; font-weight: bold;',
                name: 'displayName',
                value: '-------------',
            });
        }
        return this._displayName;
    },

    getItemsFormPanel: function (cfgPanel, cfg) {
        if (!this._itemsFormPanel) {
            cfg = core.nullValue(cfg, {});
            Ext.applyIf(
                cfg,
                {
                    activeTab: 0,
                    region: 'center',
                    border: false,
                    items: [
                        this.getNaturalPersonDataFormPanel(
                            cfgPanel,
                            {
                                managerTab: cfg.managerTab,
                                employeePk: cfg.employeePk,
                                employeeRegistry: cfg.employeeRegistry,
                                naturalPersonPk: cfg.naturalPersonPk,
                            }
                        ),
                        this.getFunctionalDataFormPanel(
                            cfgPanel,
                            {
                                managerTab: cfg.managerTab,
                                employeePk: cfg.employeePk,
                                employeeRegistry: cfg.employeeRegistry,
                                naturalPersonPk: cfg.naturalPersonPk,
                                organIdentifier: cfg.organIdentifier,
                                matriculaFieldBlocked: cfg.matriculaFieldBlocked
                            }
                        ),
                        this.getDocumentPanel(
                            cfgPanel,
                            {
                                managerTab: cfg.managerTab,
                                employeePk: cfg.employeePk,
                                employeeRegistry: cfg.employeeRegistry,
                                naturalPersonPk: cfg.naturalPersonPk,
                            }
                        ),
                        this.getDigitalDocumentPanel(
                            cfgPanel,
                            {
                                managerTab: cfg.managerTab,
                                employeePk: cfg.employeePk,
                                employeeRegistry: cfg.employeeRegistry,
                                naturalPersonPk: cfg.naturalPersonPk,
                            }
                        ),
                        this.getNomeacaoPanel(
                            cfgPanel,
                            {
                                managerTab: cfg.managerTab,
                                employeePk: cfg.employeePk,
                                employeeRegistry: cfg.employeeRegistry,
                                naturalPersonPk: cfg.naturalPersonPk,
                            }
                        ),
                        // this.getAdministrativeDocumentPanel(
                        //     cfgPanel,
                        //     {
                        //         managerTab: cfg.managerTab,
                        //         employeePk: cfg.employeePk,
                        //         employeeRegistry: cfg.employeeRegistry,
                        //         naturalPersonPk: cfg.naturalPersonPk,
                        //     }
                        // ),
                        this.getContactPanel(
                            cfgPanel,
                            {
                                managerTab: cfg.managerTab,
                                employeePk: cfg.employeePk,
                                employeeRegistry: cfg.employeeRegistry,
                                naturalPersonPk: cfg.naturalPersonPk,
                            }
                        ),
                        this.getProvisionPanel(
                            cfgPanel,
                            {
                                managerTab: cfg.managerTab,
                                employeePk: cfg.employeePk,
                                employeeRegistry: cfg.employeeRegistry,
                                naturalPersonPk: cfg.naturalPersonPk,
                                is_member: cfg.is_member,
                            }
                        ),
                        this.getMovePanel(
                            cfgPanel,
                            {
                                managerTab: cfg.managerTab,
                                employeePk: cfg.employeePk,
                                employeeRegistry: cfg.employeeRegistry,
                                naturalPersonPk: cfg.naturalPersonPk,
                            }
                        ),
                        this.getAnnotationPanel(
                            cfgPanel,
                            {
                                managerTab: cfg.managerTab,
                                employeePk: cfg.employeePk,
                                employeeRegistry: cfg.employeeRegistry,
                                naturalPersonPk: cfg.naturalPersonPk,
                            }
                        ),
                        this.getDependentPanel(
                            cfgPanel,
                            {
                                managerTab: cfg.managerTab,
                                employeePk: cfg.employeePk,
                                employeeRegistry: cfg.employeeRegistry,
                                naturalPersonPk: cfg.naturalPersonPk,
                            }
                        ),
                        this.getHealthPanel(
                            cfgPanel,
                            {
                                managerTab: cfg.managerTab,
                                employeePk: cfg.employeePk,
                                employeeRegistry: cfg.employeeRegistry,
                                naturalPersonPk: cfg.naturalPersonPk,
                            }
                        ),
                        this.getGraduationPanel(
                            cfgPanel,
                            {
                                managerTab: cfg.managerTab,
                                employeePk: cfg.employeePk,
                                employeeRegistry: cfg.employeeRegistry,
                                naturalPersonPk: cfg.naturalPersonPk,
                            }
                        ),
                        this.getResumePanel(
                            cfgPanel,
                            {
                                managerTab: cfg.managerTab,
                                employeePk: cfg.employeePk,
                                employeeRegistry: cfg.employeeRegistry,
                                naturalPersonPk: cfg.naturalPersonPk,
                            }
                        ),
                        this.getAnotherInformationPanel(
                            cfgPanel,
                            {
                                managerTab: cfg.managerTab,
                                employeePk: cfg.employeePk,
                                employeeRegistry: cfg.employeeRegistry,
                                naturalPersonPk: cfg.naturalPersonPk,
                            }
                        ),
                    ],
                }
            );
            this._itemsFormPanel = Ext._create('Ext.TabPanel', cfg);
        }
        return this._itemsFormPanel;
    },

    getNaturalPersonDataFormPanel: function (cfgPanel, cfg) {
        if (!this._naturalPersonDataFormPanel) {
            cfg = core.nullValue(cfg, {});
            Ext.apply(cfg, { title: 'Dados pessoais', });
            this._naturalPersonDataFormPanel = Ext._create('rh.employee.specialized.tab.NaturalPersonDataFormPanel', cfg);
        }
        return this._naturalPersonDataFormPanel;
    },

    getFunctionalDataFormPanel: function (cfgPanel, cfg) {
        if (!this._functionalDataFormPanel) {
            cfg = core.nullValue(cfg, {});
            Ext.apply(cfg, { title: 'Dados funcionais'});
            this._functionalDataFormPanel = Ext._create('rh.employee.specialized.tab.FunctionalDataFormPanel', cfg);
        }
        return this._functionalDataFormPanel;
    },

    getDocumentPanel: function (cfgPanel, cfg) {
        if (!this._documentPanel) {
            cfg = core.nullValue(cfg, {});
            Ext.apply(cfg, { title: 'Documentos' });
            this._documentPanel = Ext._create('rh.employee.specialized.tab.DocumentPanel', cfg);
        }
        return this._documentPanel;
    },

    getDigitalDocumentPanel: function (cfgPanel, cfg) {
        if (!this._digitalDocumentPanel) {
            cfg = core.nullValue(cfg, {});
            Ext.apply(cfg, { title: 'Documentos Digitais', });
            this._digitalDocumentPanel = Ext._create('rh.employee.specialized.tab.DigitalDocumentPanel', cfg);
        }
        return this._digitalDocumentPanel;
    },

    getNomeacaoPanel: function (cfgPanel, cfg) {
        if (!this._nomeacaoPanel) {
            cfg = core.nullValue(cfg, {});
            Ext.apply(cfg, { title: 'Documentos de Nomeações' });
            this._nomeacaoPanel = Ext._create('rh.employee.specialized.tab.NomeacaoPanel', cfg);
        }
        return this._nomeacaoPanel;
    },

    getAdministrativeDocumentPanel: function (cfgPanel, cfg) {
        if (!this._administrativeDocument) {
            cfg = core.nullValue(cfg, {});
            Ext.apply(cfg, { title: 'Arquivos Administrativos', });
            this._administrativeDocument = Ext._create('rh.employee.specialized.tab.AdministrativeDocumentPanel', cfg);
        }
        return this._administrativeDocument;
    },

    getContactPanel: function (cfgPanel, cfg) {
        if (!this._contactPanel) {
            cfg = core.nullValue(cfg, {});
            Ext.apply(cfg, { title: 'Telefone/Endereço', });
            this._contactPanel = Ext._create('rh.employee.specialized.tab.ContactPanel', cfg);
        }
        return this._contactPanel;
    },

    getHealthPanel: function (cfgPanel, cfg) {
        if (!this._healthPanel) {
            cfg = core.nullValue(cfg, {});
            Ext.apply(cfg, { title: 'Saúde', });
            this._healthPanel = Ext._create('rh.employee.specialized.tab.HealthPanel', cfg);
        }
        return this._healthPanel;
    },

    getAnotherInformationPanel: function (cfgPanel, cfg) {
        if (!this._anotherInformationPanel) {
            cfg = core.nullValue(cfg, {});
            Ext.apply(cfg, { title: 'Outras Informações', });
            this._anotherInformationPanel = Ext._create('rh.employee.specialized.tab.AnotherInformationPanel', cfg);
        }
        return this._anotherInformationPanel;
    },

    getDependentPanel: function (cfgPanel, cfg) {
        if (!this._dependentPanel) {
            cfg = core.nullValue(cfg, {});
            Ext.apply(cfg, { title: 'Dependentes/Vínculos', });
            this._dependentPanel = Ext._create('rh.employee.specialized.tab.DependentPanel', cfg);
        }
        return this._dependentPanel;
    },

    getMovePanel: function (cfgPanel, cfg) {
        if (!this._movePanel) {
            cfg = core.nullValue(cfg, {});
            Ext.apply(cfg, { title: 'Movimentações', });
            this._movePanel = Ext._create('rh.employee.specialized.tab.MovePanel', cfg);
        }
        return this._movePanel;
    },

    getProvisionPanel: function (cfgPanel, cfg) {
        if (!this._provisionPanel) {
            cfg = core.nullValue(cfg, {});
            Ext.apply(cfg, { title: 'Provimentos', is_member: cfg.is_member });
            this._provisionPanel = Ext._create('rh.employee.specialized.tab.ProvisionPanel', cfg);
        }
        return this._provisionPanel;
    },

    getAnnotationPanel: function (cfgPanel, cfg) {
        if (!this._annotationPanel) {
            cfg = core.nullValue(cfg, {});
            Ext.apply(cfg, { title: 'Anotações', });
            this._annotationPanel = Ext._create('rh.employee.specialized.tab.AnnotationPanel', cfg);
        }
        return this._annotationPanel;
    },

    getGraduationPanel: function (cfgPanel, cfg) {
        if (!this._graduationPanel) {
            cfg = core.nullValue(cfg, {});
            Ext.apply(cfg, { title: 'Formação', });
            this._graduationPanel = Ext._create('rh.employee.specialized.tab.GraduationPanel', cfg);
        }
        return this._graduationPanel;
    },

    getResumePanel: function (cfgPanel, cfg) {
        if (!this._resumePanel) {
            cfg = core.nullValue(cfg, {});
            Ext.apply(cfg, { title: 'Experiência Profissional', });
            this._resumePanel = Ext._create('rh.employee.specialized.tab.ResumePanel', cfg);
        }
        return this._resumePanel;
    },
});
