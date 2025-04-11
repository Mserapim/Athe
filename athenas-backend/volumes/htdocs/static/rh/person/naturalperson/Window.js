Ext._define('rh.person.naturalperson.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.person.naturalperson.Restful',
    width: 760,
    height: 800,

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function (instance) {
                    this.naturalPerson(instance.pk);

                    this.oId = instance.pk;
                    this.action = 'update';
                }
            }
        });

        rh.person.naturalperson.Window.superclass.constructor.call(this, cfg);

        this.naturalPerson(cfg.oId === undefined ? null : cfg.oId);
    },

    preSave: function() {   
        return this.validateMandatoryFields();
    },

    validateMandatoryFields: function () {
        var form = this.getFormPanel().getForm();
        var values = form.getValues();
            
        var camposObrigatorios = [
            { name: 'social_name',        label: 'Nome Social' },
            { name: 'nome',               label: 'Nome Registral' },
            { name: 'cpf',                label: 'CPF' },
            { name: 'data_nascimento',    label: 'Data de Nascimento' },
            { name: 'rg',                 label: 'RG' },
            { name: 'rg_orgao',           label: 'RG Órgão' },
            { name: 'rg_uf',              label: 'RG UF' },
            { name: 'rg_data_expedicao',  label: 'RG Data Expedição' }
        ];
    
        for (var i = 0; i < camposObrigatorios.length; i++) {
            var campo = camposObrigatorios[i];
            if (!values[campo.name]) {
                Ext.Msg.show({
                    title: 'Validação',
                    msg: 'O campo "' + campo.label + '" é obrigatório.',
                    buttons: Ext.Msg.OK,
                    icon: Ext.Msg.ERROR
                });
                return false;
            }
        }

        return true;
    },

    naturalPerson: function (value, prevent) {
        prevent = core.nullValue(prevent, false);

        if (value !== undefined) {
            this._naturalPerson = value;

            !prevent && this.observeNaturalPerson();
        }

        return this._naturalPerson;
    },

    observeNaturalPerson: function () {
        var value = this.naturalPerson();

        if (value) {
            this.getSpecialNeedsField().objectId(value);
            this.getSocialProgramField().objectId(value);
            this.getSeriousDiseasesField().objectId(value);

            this.getAddressGrid().enable();
            this.getAddressGrid().setParam('person', value);
            this.getAddressGrid().setFilterProperty('person', value, 100);

            this.getPhoneGrid().enable();
            this.getPhoneGrid().setParam('person', value);
            this.getPhoneGrid().setFilterProperty('person', value, 100);

            this.getDeficiencyInformationGrid().enable();
            this.getDeficiencyInformationGrid().setParam('naturalperson', value);
            this.getDeficiencyInformationGrid().setFilterProperty('naturalperson__pk', value, 100);

            this.getAnotherDocumentsField().enable();
            this.getAnotherDocumentsField().setParam('naturalpersons', value);
            this.getAnotherDocumentsField().setParam('natural_person', value);
            this.getAnotherDocumentsField().setFilterProperty('naturalpersons__id', value, 100);
            this.getAnotherDocumentsField().setFilterProperty('natural_person__id', value, 100);

            this.getAttachmentsGrid().enable();
            this.getAttachmentsGrid().setParam('person', value);
            this.getAttachmentsGrid().setFilterProperty('person__id', value, 100);

        } else {
            this.getAddressGrid().disable();
            this.getAddressGrid().setParam('person', 0);
            this.getAddressGrid().setFilterProperty('person', 0, 100, false);

            this.getPhoneGrid().disable();
            this.getPhoneGrid().setParam('person', 0);
            this.getPhoneGrid().setFilterProperty('person', 0, 100, false);

            this.getDeficiencyInformationGrid().disable();
            this.getDeficiencyInformationGrid().setParam('naturalperson', 0);
            this.getDeficiencyInformationGrid().setFilterProperty('naturalperson__pk', 0, 100, false);

            this.getAnotherDocumentsField().disable();
            this.getAnotherDocumentsField().setParam('naturalpersons', 0);
            this.getAnotherDocumentsField().setParam('natural_person', 0);
            this.getAnotherDocumentsField().setFilterProperty('naturalpersons__id', 0, 100, false);
            this.getAnotherDocumentsField().setFilterProperty('natural_person__id', 0, 100, false);

            this.getAttachmentsGrid().disable();
            this.getAttachmentsGrid().setParam('person', 0);
            this.getAttachmentsGrid().setFilterProperty('person__id', 0, 100, false);
        }
    },

    getCivilStatusField: function (cfg) {
        if (!this._civilStatus) {
            this._civilStatus = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Estado civil',
                hiddenName: 'estado_civil',
                choiceId: 'rh.MARITAL_STATUS',
                width: 424,
                allowBlank: false,
            });
            var store = this._civilStatus.getStore();
            var filter = Ext.decode(store.baseParams.filter);
            filter.push({ property: 'value__in', value: [7], stage: -1 });
            store.baseParams.filter = Ext.encode(filter);
            store.load();
        }
        return this._civilStatus;
    },

    getImmigrantResidenceTimeField: function (cfg) {
        if (!this._immigrantResidenceTimeField) {
            this._immigrantResidenceTimeField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Imigrante tempo de residência',
                hiddenName: 'immigrant_residence_time',
                choiceId: 'rh.IMMIGRANTE_RESIDENCE_TIME',
                width: 424,
                allowBlank: false,
            });
        }
        return this._immigrantResidenceTimeField;
    },

    getImmigrantEntryConditionField: function (cfg) {
        if (!this._immigrantEntryConditionField) {
            this._immigrantEntryConditionField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Imigrante condição de ingresso',
                hiddenName: 'immigrant_entry_condition',
                choiceId: 'rh.IMMIGRANTE_ENTRY_CONDITION',
                width: 424,
                allowBlank: false,
            });
        }
        return this._immigrantEntryConditionField;
    },

    getDegreeEducationChoiceField: function (cfg) {
        if (!this._degreeEducationChoiceField) {
            this._degreeEducationChoiceField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Instrução',
                hiddenName: 'grau_instrucao',
                choiceId: 'rh.DEGREE_EDUCATION',
                width: 424,
                allowBlank: false,
            });
            var store = this._degreeEducationChoiceField.getStore();
            var filter = Ext.decode(store.baseParams.filter);
            filter.push({ property: 'value__in', value: [3, 12, 13, 14], stage: -1 });
            store.baseParams.filter = Ext.encode(filter);
            store.load();
        }
        return this._degreeEducationChoiceField;
    },

    getTabMain: function (cfg) {
        if (!this._tabMain)
            this._tabMain = Ext._create('Ext.Panel', {
                layout: 'form',
                title: 'Principal',
                iconCls: 'icon-rh icon-core-main-tab',
                border: false,
                frame: true,
                scope: this,
                height: 700,
                items: [
                    {
                        layout: 'table',
                        layoutConfig: { columns: 2 },
                        xtype: 'panel',
                        flex: 1.0,
                        border: false,
                        items: [
                            {
                                layout: 'form',
                                xtype: 'panel',
                                region: 'center',
                                bodyStyle: {
                                    paddingRight: '8px'
                                },
                                items: [
                                    {
                                        xtype: 'panel',
                                        title: 'Foto',
                                        frame: true,
                                        width: 195,
                                        autoHeight: true,
                                        items: [
                                            Ext._create('core.fields.ImageFileUploadField', {
                                                hideLabel: true,
                                                name: 'foto',
                                                hideInputDisplay: true,
                                                width: 185,
                                                height: 200,
                                                captureWidth: 895,
                                                captureHeight: 555,
                                                cropWidth: (555 * 0.75),
                                                loadingOwner: this,
                                                listeners: {
                                                    scope: this,
                                                    afterchange: function (field, instance) {
                                                        var path = [
                                                            core.callAction(
                                                                'FileUploadController',
                                                                'get_image_file',
                                                                instance.file_hash
                                                            ),
                                                            '168.196'
                                                        ].join('');

                                                        var style = 'url(' + path + ') no-repeat center center';
                                                        field.ownerCt.body.dom.style.background = style;
                                                    }
                                                }
                                            })
                                        ]
                                    }
                                    ,
                                ]
                            },
                            {
                                layout: 'form',
                                xtype: 'panel',
                                region: 'center',
                                items: [
                                    {
                                        maxLength: 100,
                                        allowBlank: false,
                                        fieldLabel: 'Nome Social *',
                                        name: 'social_name',
                                        xtype: 'textfield',
                                        width: 424,
                                    },
                                    {
                                        maxLength: 100,
                                        allowBlank: false,
                                        fieldLabel: 'Nome Registral *',
                                        name: 'nome',
                                        xtype: 'textfield',
                                        width: 424,
                                    },
                                    {
                                        maxLength: 80,
                                        allowBlank: true,
                                        fieldLabel: 'Pai',
                                        name: 'nome_pai',
                                        xtype: 'textfield',
                                        width: 424,
                                    },
                                    {
                                        maxLength: 80,
                                        allowBlank: true,
                                        fieldLabel: 'Mãe',
                                        name: 'nome_mae',
                                        xtype: 'textfield',
                                        width: 424,
                                    },
                                    {
                                        allowBlank: false,
                                        fieldLabel: 'CPF *',
                                        name: 'cpf',
                                        xtype: 'cpffield',
                                        width: 200
                                    },
                                    {
                                        xtype: 'compositefield',
                                        fieldLabel: 'RG *',
                                        items: [
                                            {
                                                maxLength: 20,
                                                allowBlank: true,
                                                fieldLabel: 'RG',
                                                name: 'rg',
                                                xtype: 'textfield',
                                                width: 180
                                            },
                                            {
                                                xtype: 'displayfield',
                                                value: 'RG Órgão: *'
                                            },
                                            {
                                                maxLength: 10,
                                                allowBlank: true,
                                                fieldLabel: 'RG Órgão',
                                                width: 175,
                                                name: 'rg_orgao',
                                                xtype: 'textfield',
                                            }
                                        ]
                                    },
                                    {
                                        xtype: 'compositefield',
                                        fieldLabel: 'RG UF *',
                                        items: [
                                            {
                                                xtype: 'rest-autocompletefield',
                                                fieldLabel: 'RG UF',
                                                width: 210,
                                                allowBlank: true,
                                                rest: 'rh.estado.Restful',
                                                name: 'rg_uf'

                                            },
                                            {
                                                xtype: 'displayfield',
                                                value: 'RG Data Expedição: *'
                                            },
                                            {
                                                allowBlank: true,
                                                fieldLabel: 'RG Data Expedição',
                                                name: 'rg_data_expedicao',
                                                xtype: 'datefield',
                                                width: 95,

                                            }
                                        ]
                                    },
                                    {
                                        maxLength: 75,
                                        allowBlank: true,
                                        fieldLabel: 'Email institucional',
                                        name: 'email_institucional',
                                        xtype: 'textfield',
                                        width: 424
                                    },
                                    {
                                        maxLength: 75,
                                        allowBlank: true,
                                        fieldLabel: 'Email pessoal',
                                        name: 'email_pessoal',
                                        xtype: 'textfield',
                                        width: 424
                                    },
                                    {
                                        xtype: 'compositefield',
                                        fieldLabel: 'Data Nascimento *',
                                        width: 424,
                                        items: [
                                            {
                                                allowBlank: false,
                                                name: 'data_nascimento',
                                                xtype: 'datefield',
                                                flex: 1
                                            },
                                            {
                                                xtype: 'checkbox',
                                                fieldLabel: '&nbsp;',
                                                labelSeparator: '&nbsp;',
                                                boxLabel: 'Advogado?',
                                                allowBlank: true,
                                                scope: this,
                                                name: 'is_lawyer',
                                                field_name: 'is_lawyer',
                                                listeners: {
                                                    scope: this,
                                                    check: function (fld, checked) {
                                                        this.getOABField().setDisabled(!checked);
                                                        this.getOABField().setValue('');
                                                    },
                                                },
                                            },
                                            {
                                                xtype: 'displayfield',
                                                value: 'OAB: '
                                            },
                                            this.getOABField()
                                        ]
                                    }
                                ]
                            },
                            {
                                colspan: 2,
                                layout: 'form',
                                title: 'Endereços',
                                border: false,
                                height: 200,
                                items: [
                                    this.getAddressGrid(cfg)
                                ]
                            },
                            {
                                colspan: 2,
                                padding: '15px 0',
                                layout: 'form',
                                border: false,
                                height: 200,
                                items: [
                                    this.getPhoneGrid(cfg)
                                ]
                            }
                        ]
                    },
                ]
            });
        return this._tabMain;
    },

    getOABField: function (cfg) {
        if (!this._oabField) {
            this._oabField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'OAB',
                maxLength: 20,
                scope: this,
                allowBlank: true,
                name: 'oab',
                allowBlank: false,
                xtype: 'textfield',
                disabled: true
            });
        }
        return this._oabField;
    },

    getAnotherDocumentsField: function (cfg) {
        if (!this._anotherDocuments) {
            this._anotherDocuments = Ext._create('rh.documento.DocumentoGrid', {
                title: 'Outros Documentos',
                hideItemsToolbar: ['search', 'download'],
                region: 'center',
                scope: this,
                frame: true,
                width: 730,
                height: 350,
                gridAutoLoad: false,
                canEditCpfRg: false,
                messageToUser: 'Utilize os campos da aba Principal'
            });
        }
        return this._anotherDocuments;
    },

    getAttachmentsGrid: function (cfg) {
        if (!this._attachments) {
            this._attachments = Ext._create('rh.digitaldocument.person.Grid', {
                // title: 'Anexos',
                hideItemsToolbar: ['search', 'download'],
                region: 'center',
                scope: this,
                frame: true,
                width: 730,
                height: 650,
                gridAutoLoad: false,
            });
        }
        return this._attachments;
    },

    _getAdditionalInfo: function (cfg) {
        return [
            {
                xtype: 'rest-autocompletefield',
                fieldLabel: 'Naturalidade *',
                allowBlank: true,
                rest: 'rh.localidade.Restful',
                name: 'municipio_naturalidade',
                width: 424
            },
            {
                xtype: 'rest-autocompletefield',
                fieldLabel: 'Nacionalidade',
                allowBlank: true,
                rest: 'rh.country.Restful',
                name: 'nationality',
                width: 424
            },
            this.getCivilStatusField(cfg),
            {
                xtype: 'combo',
                fieldLabel: 'Sexo *',
                allowBlank: true,
                lazyRender: true,
                hiddenName: 'sexo',
                mode: 'local',
                triggerAction: 'all',
                store: [
                    ['F', 'FEMININO'],
                    ['M', 'MASCULINO']
                ],
                name: 'sexo',
                width: 424,
            },
            {
                fieldLabel: 'Orientação Sexual',
                xtype: 'choicefield',
                hiddenName: 'sexual_orientation',
                choiceId: 'rh.SEXUAL_ORIENTATION',
                width: 424,
            },
            {
                fieldLabel: 'Raça/Cor',
                xtype: 'choicefield',
                hiddenName: 'raca_cor',
                choiceId: 'rh.TYPE_RACE',
                width: 424,
            },
            {
                xtype: 'textfield',
                fieldLabel: 'Gênero',
                allowBlank: true,
                name: 'genero',
                width: 424,
            },
            this.getDegreeEducationChoiceField(cfg),
            {
                xtype: 'checkbox',
                fieldLabel: '&nbsp;',
                labelSeparator: '&nbsp;',
                boxLabel: 'Habilita Protocolo?',
                allowBlank: true,
                name: 'enable_protocol'
            },
            this.getAnotherDocumentsField(cfg)
        ];
    },

    getTabAdditionalInfo: function (cfg) {
        if (!this._tabDocuments)
            this._tabDocuments = Ext._create('Ext.Panel', {
                layout: 'form',
                title: 'Informações Complementares',
                iconCls: 'icon-rh icon-core-documents-tab',
                border: false,
                frame: true,
                scope: this,
                height: 550,
                items: this._getAdditionalInfo(cfg)
            });
        return this._tabDocuments;
    },

    getPhoneGrid: function (cfg) {
        if (!this._phoneGrid) {
            this._phoneGrid = Ext._create('rh.telefone.TelefoneGrid', {
                hideItemsToolbar: ['search', 'download'],
                title: 'Telefones',
                region: 'center',
                frame: true,
                scope: this,
                height: 180,
                columnAction: false,
            });
        }
        return this._phoneGrid;
    },

    getSpecialNeedsField: function (cfg) {
        if (!this._specialNeedsField)
            this._specialNeedsField = Ext._create('core.fields.RelatedRestfulField', {
                title: 'Necessidades especiais',
                xtype: 'rest-relatedfield',
                hideLabel: true,
                name: 'necessidades_especiais',
                displayField: 'unicode',
                allowBlank: false,
                relatedname: 'pessoa',
                rest: this.rest,
                sourceRest: 'rh.necessidadeespecial.Restful',
                oId: this.oId || cfg.oId,
                width: 740,
                height: 345,
                border: false
            });

        return this._specialNeedsField;
    },

    getSeriousDiseasesField: function (cfg) {
        if (!this._seriousDiseasesField)
            this._seriousDiseasesField = Ext._create('core.fields.RelatedRestfulField', {
                xtype: 'rest-relatedfield',
                title: 'Doenças Graves',
                hideLabel: true,
                name: 'serious_diseases',
                displayField: 'name',
                allowBlank: false,
                relatedname: 'in_pessoafisica',
                rest: this.rest,
                sourceRest: 'rh.seriousdiseases.Restful',
                oId: this.oId || cfg.oId,
                width: 740,
                height: 345,
                border: false
            });

        return this._seriousDiseasesField;
    },

    getDeficiencyInformationGrid: function (cfg) {
        if (!this._deficiencyInformationGrid)
            this._deficiencyInformationGrid = Ext._create('rh.deficiencyinformation.Grid', {
                title: 'Informações de deficiência',
                hideItemsToolbar: ['search', 'download'],
                region: 'center',
                scope: this,
                columnAction: false,
                width: 725,
                height: 325,
                border: false
            });
        return this._deficiencyInformationGrid;
    },

    getHealthDetailsPanel: function (cfg) {
        if (!this._healthDetailsPanel)
            this._healthDetailsPanel = Ext._create('Ext.Panel', {
                border: false,
                autoHeight: true,
                items: [
                    new Ext.TabPanel({
                        activeTab: 0,
                        tabPosition: 'top',
                        border: false,
                        items: [
                            this.getSpecialNeedsField(cfg),
                            this.getSeriousDiseasesField(cfg),
                            this.getDeficiencyInformationGrid(cfg)
                        ]
                    })
                ]
            });

        return this._healthDetailsPanel;
    },

    getTabHealth: function (cfg) {
        if (!this._tabHealth)
            this._tabHealth = Ext._create('Ext.Panel', {
                layout: 'form',
                title: 'Saúde',
                iconCls: 'icon-rh icon-core-health-tab',
                border: false,
                frame: true,
                scope: this,
                height: 530,
                items: [
                    {
                        fieldLabel: 'Sangue',
                        xtype: 'choicefield',
                        hiddenName: 'sangue',
                        choiceId: 'rh.BLOOD',
                        width: 600,
                        value: 5
                    },
                    {
                        fieldLabel: 'Fator RH',
                        xtype: 'choicefield',
                        hiddenName: 'fator_rh',
                        choiceId: 'rh.FACTOR_RH',
                        width: 600,
                        value: 3
                    },
                    {
                        allowBlank: true,
                        fieldLabel: 'Data óbito',
                        name: 'data_obito',
                        xtype: 'datefield',
                        width: 600
                    },
                    {
                        xtype: 'checkbox',
                        fieldLabel: '&nbsp;',
                        labelSeparator: '&nbsp;',
                        boxLabel: 'Doador de órgãos?',
                        allowBlank: true,
                        name: 'doador',
                    },
                    {
                        xtype: 'checkbox',
                        fieldLabel: '&nbsp;',
                        labelSeparator: '&nbsp;',
                        boxLabel: 'Necessidade Especial?',
                        allowBlank: true,
                        name: 'necessidade_especial'
                    },
                    {
                        xtype: 'checkbox',
                        fieldLabel: '&nbsp;',
                        labelSeparator: '&nbsp;',
                        boxLabel: 'Doença Grave?',
                        allowBlank: true,
                        name: 'has_serious_diseases'
                    },
                    this.getHealthDetailsPanel(cfg)
                ]
            });
        return this._tabHealth;
    },

    getSocialProgramField: function (cfg) {
        if (!this._socialProgramField)
            this._socialProgramField = Ext._create('core.fields.RelatedRestfulField', {
                xtype: 'rest-relatedfield',
                title: 'Programas Sociais',
                hideLabel: true,
                name: 'social_program',
                displayField: 'name',
                allowBlank: false,
                relatedname: 'in_pessoafisica',
                rest: this.rest,
                sourceRest: 'rh.socialprogram.Restful',
                oId: this.oId || cfg.oId,
                width: 740,
                height: 490,
                border: false
            });

        return this._socialProgramField;
    },

    getTabSocioeconomic: function (cfg) {
        if (!this._tabSocioeconomic)
            this._tabSocioeconomic = Ext._create('Ext.Panel', {
                layout: 'form',
                title: 'Socioeconômico',
                iconCls: 'icon-rh icon-core-socioeconomic-tab',
                border: false,
                frame: true,
                scope: this,
                height: 550,
                items: [
                    {
                        maxLength: 20,
                        allowBlank: true,
                        fieldLabel: 'Renda Familiar',
                        name: 'renda_familiar',
                        xtype: 'textfield',
                        width: 600
                    },
                    this.getSocialProgramField(cfg)
                ]
            });
        return this._tabSocioeconomic;
    },

    getTabImmigrant: function (cfg) {
        if (!this._tabImmigrant)
            this._tabImmigrant = Ext._create('Ext.Panel', {
                layout: 'form',
                title: 'Imigrante',
                iconCls: 'icon-core icon-core-set-employee',
                border: false,
                frame: true,
                scope: this,
                height: 550,
                items: [
                    this.getImmigrantResidenceTimeField(cfg),
                    this.getImmigrantEntryConditionField(cfg)
                ]
            });
        return this._tabImmigrant;
    },

    getAddressGrid: function (cfg) {
        if (!this._addressGrid) {
            this._addressGrid = Ext._create('rh.endereco.EnderecoGrid', {
                hideItemsToolbar: ['search', 'download'],
                region: 'center',
                scope: this,
                frame: true,
                height: 170,
                columnAction: false,
            });
        }
        return this._addressGrid;
    },

    getTabAttachments: function (cfg) {
        if (!this._tabAttachments)
            this._tabAttachments = Ext._create('Ext.Panel', {
                layout: 'form',
                title: 'Anexos',
                iconCls: 'icon-rh icon-core-contacts-tab',
                border: false,
                frame: true,
                scope: this,
                height: 730,
                items: [
                    this.getAttachmentsGrid(cfg)
                ]
            });
        return this._tabAttachments;
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                width: 750,
                items: [
                    new Ext.TabPanel({
                        activeTab: 0,
                        tabPosition: 'top',
                        border: false,
                        items: [
                            this.getTabMain(cfg),
                            this.getTabAdditionalInfo(cfg),
                            this.getTabAttachments(cfg),
                            this.getTabHealth(cfg),
                            this.getTabSocioeconomic(cfg),
                            this.getTabImmigrant(cfg)
                        ]
                    })
                ]
            });

        return this._formPanel;
    }
});

rh.person.Grid.register(
    'pessoafisica',
    'Pessoa Física',
    'icon-rh icon-core-natural-person',
    'rh.person.naturalperson.Window'
);
