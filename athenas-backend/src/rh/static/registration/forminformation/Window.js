Ext.ns('rh.registration');

Ext._define('rh.registration.forminformation.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.registration.forminformation.Restful',

    width: 1000,
    height: 700,

    autoScroll: true,

    statics: {
        STATE_EMPLOYEE_EDITION: 1,
        STATE_EMPLOYEE_VALIDATED_PROBLEM: 4,
        STATE_EMPLOYEE_VALIDATED: 5,
        STATE_DGPFP_SENT: 2,
        STATE_DGPFP_RECEIVED: 3,
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                buttonAlign: 'right',
                disableSaveAndNew: true,
                saveAndContinue: {
                    scope: this,
                    fn: function (instance) {
                        this.oId = instance.pk;
                        this.action = 'update';
                        this.setPendenciesValues(instance);
                    }
                },
                border: false
            }, 
            this.getDependentGrid()
        );

        rh.registration.forminformation.Window.superclass.constructor.call(this, cfg);
        this.getFormGed().setForm(cfg.oId === undefined ? null : cfg.oId);

        this.on({
            scope: this,
            afterrender: function () { this._markInvalidAfterRender(cfg.values) }
        });
        this._observe();
    },

    _observe: function () {
        var _outsider = this.getOutsiderField().getValue();
        if (_outsider == undefined || _outsider == false) {
            this.getOutsiderCittyField().setVisible(false);
            this.getCountyField().setVisible(true);
            this.getCountryField().setVisible(false);

            this.getTypeStreetChoiceField().setReadOnly(false);
            this.getNeighborhoodField().allowBlank = false;
            this.getCEPField().allowBlank = true;
            this.getCountyField().allowBlank = false;

            this.getTypeStreetChoiceField().setValue(0);
            this.getCountryField().setVisible('');
        }
        else {
            this.getTypeStreetChoiceField().setReadOnly(true);
            this.getNeighborhoodField().allowBlank = true;
            this.getCEPField().allowBlank = false;
            this.getCountyField().allowBlank = true;

            this.getOutsiderCittyField().setVisible(true);
            this.getCountyField().setVisible(false);
            this.getCountryField().setVisible(true);

            this.getTypeStreetChoiceField().setValue(100);
            this.getCountyField().setValue('');
        }
    },

    _prepareSuccessCallback: function (callback, closeSuccess) {
        return rh.registration.forminformation.Window.superclass._prepareSuccessCallback.call(this, callback, true);
    },

    save: function (close, sendValidation) {
        this.setInternationalPhone();
        if (sendValidation) {
            var wnd = this;
            this.callback = {
                success: {
                    scope: this,
                    fn: function (instance) {
                        wnd.ownerGrid.sendValidation(instance.pk, wnd);
                    }
                }
            };
        }

        rh.registration.forminformation.Window.superclass.save.call(this, close);
    },

    setPendenciesValues: function (instance) {
        var form = this.getFormPanel().getForm();
        this.getPendencyField().setValue(instance.pendency)
        this.setPendenciesCount(instance.pendency_errors_total)
    },

    setPendenciesCount: function (total) {
        if (total > 0) {
            this.tabPendency().setTitle('<b>Pendências</b> <img src="static/images/icons/warn.png" width="13" height="13"/>')
        } else {
            this.tabPendency().setTitle('<b>Pendências</b> <img src="static/images/icons/success.png" width="13" height="13" />')
        }
    },

    _markInvalidAfterRender: function (instance) {
        var errors = Ext.decode(instance.pendency_errors);
        if (errors) {
            var me = this;
            this.setPendenciesCount(instance.pendency_errors_total);
            errors.forEach(
                function (error) {
                    var field = me.getFormPanel().getForm().findField(error.field);
                    if (field != undefined && field.xtype == 'rest-autocompletefield')
                        field = field.getComboField();

                    if (field) {
                        var tpl = new Ext.XTemplate(
                            '<ul>',
                            '<tpl for="values">',
                            '<li>{.}</li>',
                            '</tpl>',
                            '</ul>'
                        );

                        field.markInvalid(tpl.apply(error));
                    }
                }
            );
        }
    },

    getFormGed: function () {
        if (!this._gedGrid)
            this._gedGrid = Ext._create('rh.registration.forminformation.ged.Grid', {
                title: 'Anexo(s)',
                layout: 'form',
                height: 230,
                anchor: '100% 100%',
                border: false,
            });
        return this._gedGrid;
    },

    getColorBackgroud: function (state, diff) {
        var color = '';
        if (diff == true && state == rh.registration.forminformation.Window.STATE_EMPLOYEE_VALIDATED_PROBLEM)
            color = 'background-color: #FF6347;';
        else if (diff == true && state != rh.registration.forminformation.Window.STATE_EMPLOYEE_VALIDATED_PROBLEM)
            color = 'background-color: #6495ED;';
        return color;
    },

    setInternationalPhone: function () {
        if (this.getPhoneOutsiderField().originalValue != this.getPhoneOutsiderField().getValue()) {
            if (this.getPhoneOutsiderField().getValue() == true) {
                this.getPhoneField().getHiddenField().setValue(this.getPhoneInternationalField().getValue())
            } else {
                this.getPhoneInternationalField().setValue(this.getPhoneField().getHiddenField().getValue())
            }

        }
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: [
                    {
                        xtype: 'tabpanel',
                        border: false,
                        activeTab: 0,
                        items: [
                            {
                                title: 'Informações',
                                layout: 'border',
                                border: false,
                                width: '100%',
                                height: '100%',
                                style: 'background-color: #fff',
                                height: 2300,
                                items: [
                                    {
                                        region: 'west',
                                        border: false,
                                        width: 530,
                                        items: [
                                            {
                                                xtype: 'fieldset',
                                                title: 'Observação',
                                                hidden: (cfg.values.state == this.STATE_EMPLOYEE_VALIDATED_PROBLEM ? false : true),
                                                items: [
                                                    {
                                                        xtype: 'displayfield',
                                                        value: '<b>* Os campos grifados em vermelho não foram validados pelo DGPFP;</b>',
                                                    }
                                                ]
                                            },
                                            {
                                                xtype: 'fieldset',
                                                title: 'Dados pessoais',
                                                name: 'fieldServidor',
                                                items: [
                                                    {
                                                        xtype: 'textfield',
                                                        width: 400,
                                                        enableKeyEvents: true,
                                                        name: 'nome',
                                                        fieldLabel: 'Nome',
                                                        style: this.getColorBackgroud(cfg.values.state, cfg.values.nome_diff)
                                                    },
                                                    {
                                                        xtype: 'textfield',
                                                        width: 400,
                                                        enableKeyEvents: true,
                                                        name: 'social_name',
                                                        fieldLabel: 'Nome Social',
                                                        style: this.getColorBackgroud(cfg.values.state, cfg.values.social_name_diff)
                                                    },
                                                    {
                                                        xtype: 'textfield',
                                                        width: 400,
                                                        enableKeyEvents: true,
                                                        name: 'nome_conjuge',
                                                        fieldLabel: 'Nome Cônjuge/ Companheiro',
                                                        style: this.getColorBackgroud(cfg.values.state, cfg.values.nome_conjuge_diff)
                                                    },
                                                    {
                                                        xtype: 'textfield',
                                                        width: 400,
                                                        enableKeyEvents: true,
                                                        name: 'nome_mae',
                                                        fieldLabel: 'Nome da Mãe',
                                                        style: this.getColorBackgroud(cfg.values.state, cfg.values.nome_mae_diff)
                                                    },
                                                    {
                                                        xtype: 'textfield',
                                                        width: 400,
                                                        enableKeyEvents: true,
                                                        name: 'nome_pai',
                                                        fieldLabel: 'Nome do Pai',
                                                        style: this.getColorBackgroud(cfg.values.state, cfg.values.nome_pai_diff)
                                                    },
                                                    // {
                                                    //     xtype: 'combo',
                                                    //     width: 400,
                                                    //     enableKeyEvents: true,
                                                    //     allowBlank: true,
                                                    //     mode: 'local',
                                                    //     triggerAction: 'all',
                                                    //     name: 'genero',
                                                    //     store: [
                                                    //         ['HOMEM CIS', 'HOMEM CIS'],
                                                    //         ['MULHER CIS', 'MULHER CIS'],
                                                    //         ['HOMEM TRANS', 'HOMEM TRANS'],
                                                    //         ['MULHER TRANS', 'MULHER TRANS'],
                                                    //         ['OUTROS', 'OUTROS']
                                                    //     ],
                                                    //     fieldLabel: 'Identidade de Gênero',
                                                    //     style: this.getColorBackgroud(cfg.values.state, cfg.values.genero_diff)
                                                    // },
                                                    {
                                                        layout: 'hbox',
                                                        border: false,
                                                        items: [
                                                            {
                                                                layout: 'form',
                                                                region: 'center',
                                                                border: false,
                                                                items: [
                                                                    {
                                                                        xtype: 'combo',
                                                                        fieldLabel: 'Sexo',
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
                                                                        width: 140,
                                                                        style: this.getColorBackgroud(cfg.values.state, cfg.values.sexo_diff)
                                                                    }
                                                                ]
                                                            },
                                                            // {
                                                            //     layout: 'form',
                                                            //     region: 'center',
                                                            //     border: false,
                                                            //     style: 'margin-left: 5px',
                                                            //     items:
                                                            //         [
                                                            //             {
                                                            //                 fieldLabel: 'Orientação Sexual',
                                                            //                 xtype: 'choicefield',
                                                            //                 choiceId: 'rh.SEXUAL_ORIENTATION',
                                                            //                 hiddenName: 'sexual_orientation',
                                                            //                 name: 'sexual_orientation',
                                                            //                 width: 148,
                                                            //                 style: this.getColorBackgroud(cfg.values.state, cfg.values.sexual_orientation_diff)
                                                            //             }
                                                            //         ]
                                                            // }
                                                        ]
                                                    },
                                                    {
                                                        layout: 'hbox',
                                                        border: false,
                                                        items: [
                                                            {
                                                                layout: 'form',
                                                                region: 'center',
                                                                border: false,
                                                                items:
                                                                    [
                                                                        this.getMaritalStatusChoiceField(cfg)
                                                                    ]
                                                            },
                                                            {
                                                                layout: 'form',
                                                                region: 'center',
                                                                border: false,
                                                                style: 'margin-left: 5px',
                                                                items:
                                                                    [
                                                                        {
                                                                            fieldLabel: 'Possui União Estável ?',
                                                                            xtype: "checkbox",
                                                                            name: 'uniao_estavel',
                                                                            width: 55,
                                                                            style: 'margin-left: -65px',
                                                                            style: this.getColorBackgroud(cfg.values.state, cfg.values.doador_diff),
                                                                        }
                                                                    ]
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        layout: 'hbox',
                                                        border: false,
                                                        items: [
                                                            {
                                                                layout: 'form',
                                                                region: 'center',
                                                                border: false,
                                                                items: [this.getBloodChoiceField({}, cfg.values)]
                                                            },
                                                            {
                                                                layout: 'form',
                                                                region: 'center',
                                                                border: false,
                                                                style: 'margin-left: 5px',
                                                                items: this.getFactorRhCoiceField({}, cfg.values)
                                                            },
                                                            {
                                                                layout: 'form',
                                                                region: 'center',
                                                                border: false,
                                                                style: 'margin-left: 15px',
                                                                items:
                                                                {
                                                                    fieldLabel: 'Doador',
                                                                    xtype: "checkbox",
                                                                    name: 'doador',
                                                                    width: 55,
                                                                    style: 'margin-left: -65px',
                                                                    style: this.getColorBackgroud(cfg.values.state, cfg.values.doador_diff) + 'margin-left: -45px',
                                                                }
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        xtype: 'rest-autocompletefield',
                                                        fieldLabel: 'Naturalidade',
                                                        name: 'municipio_naturalidade',
                                                        displayField: 'unicode',
                                                        allowBlank: true,
                                                        rest: 'rh.localidade.Restful',
                                                        width: 400,
                                                        style: this.getColorBackgroud(cfg.values.state, cfg.values.municipio_naturalidade_diff)
                                                    },
                                                    {
                                                        xtype: 'rest-autocompletefield',
                                                        fieldLabel: 'Nacionalidade',
                                                        name: 'nationality',
                                                        displayField: 'unicode',
                                                        allowBlank: true,
                                                        rest: 'rh.country.Restful',
                                                        width: 400,
                                                        style: this.getColorBackgroud(cfg.values.state, cfg.values.nationality_diff)
                                                    },
                                                    {
                                                        xtype: 'rest-autocompletefield',
                                                        fieldLabel: 'País de nascimento',
                                                        name: 'nationality_birth',
                                                        displayField: 'unicode',
                                                        allowBlank: true,
                                                        rest: 'rh.country.Restful',
                                                        width: 400,
                                                        style: this.getColorBackgroud(cfg.values.state, cfg.values.nationality_birth_diff)
                                                    },
                                                    {
                                                        xtype: 'textfield',
                                                        width: 400,
                                                        enableKeyEvents: true,
                                                        name: 'email_institucional',
                                                        fieldLabel: 'E-mail Institucional',
                                                        style: this.getColorBackgroud(cfg.values.state, cfg.values.email_institucional_diff)
                                                    },
                                                    {
                                                        layout: 'hbox',
                                                        border: false,
                                                        items: [
                                                            {
                                                                layout: 'form',
                                                                region: 'center',
                                                                border: false,
                                                                items:
                                                                    [
                                                                        {
                                                                            name: "data_nascimento",
                                                                            fieldLabel: "Data de Nascimento",
                                                                            xtype: "datefield",
                                                                            allowBlank: true,
                                                                            width: 140,
                                                                            style: this.getColorBackgroud(cfg.values.state, cfg.values.data_nascimento_diff)
                                                                        },
                                                                    ]
                                                            },
                                                            {
                                                                layout: 'form',
                                                                region: 'center',
                                                                border: false,
                                                                style: 'margin-left: 5px',
                                                                items:
                                                                    [
                                                                        {
                                                                            fieldLabel: 'Raça/Cor',
                                                                            xtype: 'choicefield',
                                                                            hiddenName: 'raca_cor',
                                                                            name: 'raca_cor',
                                                                            choiceId: 'rh.TYPE_RACE',
                                                                            width: 148,
                                                                            style: this.getColorBackgroud(cfg.values.state, cfg.values.raca_cor_diff)
                                                                        }
                                                                    ]
                                                            },
                                                        ]
                                                    },
                                                    // {
                                                    //     layout: 'form',
                                                    //     region: 'center',
                                                    //     border: false,
                                                    //     items:
                                                    //         [
                                                    //             {
                                                    //                 fieldLabel: 'Grau de Instrução',
                                                    //                 xtype: 'choicefield',
                                                    //                 choiceId: 'rh.DEGREE_EDUCATION',
                                                    //                 hiddenName: 'grau_instrucao',
                                                    //                 name: 'grau_instrucao',
                                                    //                 width: 400,
                                                    //                 style: this.getColorBackgroud(cfg.values.state, cfg.values.grau_instrucao_diff)
                                                    //             }
                                                    //         ]
                                                    // }
                                                ]
                                            },
                                            {
                                                xtype: 'fieldset',
                                                title: 'Endereço',
                                                name: 'fieldEndereço',
                                                items: [
                                                    this.getOutsiderField({}, cfg.values),
                                                    this.getCountyField({}, cfg.values),
                                                    this.getOutsiderCittyField({}, cfg.values),
                                                    {
                                                        layout: 'hbox',
                                                        border: false,
                                                        items: [
                                                            {
                                                                layout: 'form',
                                                                region: 'center',
                                                                border: false,
                                                                items:
                                                                    [
                                                                        this.getTypeAddressChoiceField({}, cfg.values)
                                                                    ]
                                                            },
                                                            {
                                                                layout: 'form',
                                                                region: 'center',
                                                                border: false,
                                                                style: 'margin-left: 5px',
                                                                items:
                                                                    [
                                                                        this.getTypeStreetChoiceField({}, cfg.values)
                                                                    ]
                                                            }
                                                        ]
                                                    },
                                                    this.getPublicPlaceField({}, cfg.values),
                                                    {
                                                        layout: 'hbox',
                                                        border: false,
                                                        items: [
                                                            {
                                                                layout: 'form',
                                                                region: 'center',
                                                                border: false,
                                                                items:
                                                                    [
                                                                        this.getNumberField({}, cfg.values)
                                                                    ]
                                                            },
                                                            {
                                                                layout: 'form',
                                                                region: 'center',
                                                                border: false,
                                                                style: 'margin-left: 5px',
                                                                items:
                                                                    [
                                                                        this.getCEPField({}, cfg.values)
                                                                    ]
                                                            }
                                                        ]
                                                    },
                                                    this.getNeighborhoodField({}, cfg.values),
                                                    this.getComplementField({}, cfg.values),
                                                    this.getCountryField({}, cfg.values),
                                                    this.getNewAddressField({}, cfg.values),
                                                ]
                                            },
                                            {
                                                xtype: 'fieldset',
                                                title: 'Telefone',
                                                name: 'fieldServidor',
                                                items: [
                                                    this.getPhoneOutsiderField({}, cfg.values),
                                                    this.getPhoneField({}, cfg.values),
                                                    this.getPhoneInternationalField({}, cfg.values),
                                                    {
                                                        layout: 'hbox',
                                                        border: false,
                                                        items: [
                                                            {
                                                                layout: 'form',
                                                                region: 'center',
                                                                border: false,
                                                                items:
                                                                    [
                                                                        {
                                                                            fieldLabel: 'Nome Emergência',
                                                                            xtype: 'textfield',
                                                                            hiddenName: 'contact_emergency_name',
                                                                            name: 'contact_emergency_name',
                                                                            enableKeyEvents: true,
                                                                            maxLength: 60,
                                                                            width: 140,
                                                                            style: this.getColorBackgroud(cfg.values.state, cfg.values.contact_emergency_name_diff)
                                                                        },
                                                                    ]
                                                            },
                                                            
                                                            {
                                                                layout: 'form',
                                                                region: 'center',
                                                                border: false,
                                                                style: 'margin-left: 5px',
                                                                items:
                                                                    [
                                                                        this.getContactEmergencyPhoneField({}, cfg.values)
                                                                    ]
                                                            }
                                                        ]
                                                    }, 
                                                    {
                                                        layout: 'hbox',
                                                        border: false,
                                                        items: 
                                                        [
                                                            {
                                                            layout: 'form',
                                                            region: 'center',
                                                            border: false,
                                                            items:
                                                                [
                                                                    {
                                                                        fieldLabel: 'Grau de Parentesco do Contato Emergência',
                                                                        xtype: 'textfield',
                                                                        hiddenName: 'contact_emergency_phone_kinship',
                                                                        name: 'contact_emergency_phone_kinship',
                                                                        enableKeyEvents: true,
                                                                        maxLength: 60,
                                                                        width: 140,
                                                                        style: this.getColorBackgroud(cfg.values.state, cfg.values.contact_emergency_phone_kinship_diff)
                                                                    },
                                                                ]
                                                            },    
                                                        ]
                                                    }
                                                    
                                                ]
                                            },
                                            {
                                                xtype: 'fieldset',
                                                title: 'Documentos',
                                                name: 'fieldServidor',
                                                items: [
                                                    {
                                                        xtype: 'fieldset',
                                                        title: 'CPF',
                                                        name: 'fieldCPF',
                                                        items: [
                                                            {
                                                                xtype: 'cpffield',
                                                                width: 370,
                                                                enableKeyEvents: true,
                                                                name: 'cpf',
                                                                fieldLabel: 'CPF',
                                                                readOnly: true,
                                                                disabled: true,
                                                            },
                                                        ]
                                                    },
                                                    {
                                                        xtype: 'fieldset',
                                                        title: 'Registro Geral (RG)',
                                                        items: [
                                                            {
                                                                xtype: 'textfield',
                                                                width: 375,
                                                                enableKeyEvents: true,
                                                                name: 'rg',
                                                                fieldLabel: 'Número',
                                                                style: this.getColorBackgroud(cfg.values.state, cfg.values.rg_diff)
                                                            },
                                                            {
                                                                layout: 'hbox',
                                                                border: false,
                                                                items: [
                                                                    {
                                                                        layout: 'form',
                                                                        region: 'center',
                                                                        border: false,
                                                                        items:
                                                                            [
                                                                                {
                                                                                    fieldLabel: 'Órgão',
                                                                                    xtype: 'textfield',
                                                                                    hiddenName: 'rg_orgao',
                                                                                    name: 'rg_orgao',
                                                                                    enableKeyEvents: true,
                                                                                    width: 130,
                                                                                    style: this.getColorBackgroud(cfg.values.state, cfg.values.rg_orgao_diff)
                                                                                },
                                                                            ]
                                                                    },
                                                                    {
                                                                        layout: 'form',
                                                                        region: 'center',
                                                                        border: false,
                                                                        style: 'margin-left: 5px',
                                                                        items:
                                                                            [
                                                                                {
                                                                                    name: "rg_data_expedicao",
                                                                                    fieldLabel: "Data de Expedição",
                                                                                    xtype: "datefield",
                                                                                    allowBlank: true,
                                                                                    width: 133,
                                                                                    style: this.getColorBackgroud(cfg.values.state, cfg.values.rg_data_expedicao_diff)
                                                                                }
                                                                            ]
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                xtype: 'rest-autocompletefield',
                                                                fieldLabel: 'UF',
                                                                name: 'rg_uf',
                                                                displayField: 'unicode',
                                                                allowBlank: true,
                                                                rest: 'rh.estado.Restful',
                                                                width: 375,
                                                                style: this.getColorBackgroud(cfg.values.state, cfg.values.rg_uf_diff)
                                                            },
                                                        ]
                                                    },
                                                    {
                                                        xtype: 'fieldset',
                                                        title: 'CNH',
                                                        items: [
                                                            {
                                                                fieldLabel: 'Número',
                                                                xtype: 'textfield',
                                                                hiddenName: 'cnh',
                                                                name: 'cnh',
                                                                enableKeyEvents: true,
                                                                width: 371,
                                                                maxLength: 11,
                                                                minLength: 11,
                                                                style: this.getColorBackgroud(cfg.values.state, cfg.values.cnh_diff)
                                                            },
                                                            {
                                                                layout: 'hbox',
                                                                border: false,
                                                                items: [
                                                                    {
                                                                        layout: 'form',
                                                                        region: 'center',
                                                                        border: false,
                                                                        items:
                                                                            [
                                                                                {
                                                                                    name: "cnh_first_date",
                                                                                    fieldLabel: "Primeira Data Expedição",
                                                                                    xtype: "datefield",
                                                                                    allowBlank: true,
                                                                                    width: 141,
                                                                                    style: this.getColorBackgroud(cfg.values.state, cfg.values.cnh_first_date_diff)
                                                                                }
                                                                            ]
                                                                    },
                                                                    {
                                                                        layout: 'form',
                                                                        region: 'center',
                                                                        border: false,
                                                                        style: 'margin-left: 5px',
                                                                        items:
                                                                            [
                                                                                {
                                                                                    fieldLabel: 'Categoria',
                                                                                    xtype: 'textfield',
                                                                                    hiddenName: 'cnh_categoria',
                                                                                    name: 'cnh_categoria',
                                                                                    enableKeyEvents: true,
                                                                                    width: 119,
                                                                                    style: this.getColorBackgroud(cfg.values.state, cfg.values.cnh_categoria_diff)
                                                                                }
                                                                            ]
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                layout: 'hbox',
                                                                border: false,
                                                                items: [
                                                                    {
                                                                        layout: 'form',
                                                                        region: 'center',
                                                                        border: false,
                                                                        items:
                                                                            [
                                                                                {
                                                                                    name: "cnh_expedition_date",
                                                                                    fieldLabel: "Data de Expedição",
                                                                                    xtype: "datefield",
                                                                                    allowBlank: true,
                                                                                    width: 140,
                                                                                    style: this.getColorBackgroud(cfg.values.state, cfg.values.cnh_expedition_date_diff)
                                                                                }
                                                                            ]
                                                                    },
                                                                    {
                                                                        layout: 'form',
                                                                        region: 'center',
                                                                        border: false,
                                                                        style: 'margin-left: 5px',
                                                                        items:
                                                                            [
                                                                                {
                                                                                    name: "cnh_validity_date",
                                                                                    fieldLabel: "Data de Validade",
                                                                                    xtype: "datefield",
                                                                                    allowBlank: true,
                                                                                    width: 123,
                                                                                    style: this.getColorBackgroud(cfg.values.state, cfg.values.cnh_validity_date_diff)
                                                                                }
                                                                            ]
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                layout: 'hbox',
                                                                border: false,
                                                                items: [
                                                                    {
                                                                        layout: 'form',
                                                                        region: 'center',
                                                                        border: false,
                                                                        items:
                                                                            [
                                                                                {
                                                                                    xtype: 'rest-autocompletefield',
                                                                                    fieldLabel: 'UF',
                                                                                    hiddenName: 'cnh_state',
                                                                                    name: 'cnh_state',
                                                                                    displayField: 'unicode',
                                                                                    allowBlank: true,
                                                                                    validateOnBlur: true,
                                                                                    width: 375,
                                                                                    rest: 'rh.estado.Restful',
                                                                                    style: this.getColorBackgroud(cfg.values.state, cfg.values.cnh_state_diff)
                                                                                }
                                                                            ]
                                                                    },
                                                                ]
                                                            },
                                                        ]
                                                    },
                                                    {
                                                        xtype: 'fieldset',
                                                        title: 'Carteira de Trabalho(CTPS)',
                                                        items: [
                                                            {
                                                                layout: 'hbox',
                                                                border: false,
                                                                items: [
                                                                    {
                                                                        layout: 'form',
                                                                        region: 'center',
                                                                        border: false,
                                                                        items:
                                                                            [
                                                                                {
                                                                                    fieldLabel: 'Número',
                                                                                    xtype: 'textfield',
                                                                                    hiddenName: 'ctps',
                                                                                    name: 'ctps',
                                                                                    enableKeyEvents: true,
                                                                                    width: 140,
                                                                                    style: this.getColorBackgroud(cfg.values.state, cfg.values.ctps_diff)
                                                                                },
                                                                            ]
                                                                    },
                                                                    {
                                                                        layout: 'form',
                                                                        region: 'center',
                                                                        border: false,
                                                                        style: 'margin-left: 5px',
                                                                        items:
                                                                            [
                                                                                {
                                                                                    fieldLabel: 'Série',
                                                                                    xtype: 'textfield',
                                                                                    hiddenName: 'serie_ctps',
                                                                                    name: 'serie_ctps',
                                                                                    enableKeyEvents: true,
                                                                                    width: 120,
                                                                                    style: this.getColorBackgroud(cfg.values.state, cfg.values.serie_ctps_diff)
                                                                                }
                                                                            ]
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                xtype: 'rest-autocompletefield',
                                                                fieldLabel: 'UF',
                                                                name: 'ctps_state',
                                                                displayField: 'unicode',
                                                                allowBlank: true,
                                                                rest: 'rh.estado.Restful',
                                                                width: 375,
                                                                style: this.getColorBackgroud(cfg.values.state, cfg.values.ctps_state_diff)
                                                            },
                                                        ]
                                                    },
                                                    {
                                                        xtype: 'fieldset',
                                                        title: 'PIS/PASEP',
                                                        items: [
                                                            {
                                                                xtype: 'textfield',
                                                                width: 375,
                                                                enableKeyEvents: true,
                                                                name: 'pis_pasep',
                                                                fieldLabel: 'Número',
                                                                style: this.getColorBackgroud(cfg.values.state, cfg.values.pis_pasep_diff),
                                                            },
                                                        ]
                                                    },
                                                    {
                                                        xtype: 'fieldset',
                                                        title: 'Reservista',
                                                        items: [
                                                            {
                                                                layout: 'hbox',
                                                                border: false,
                                                                items: [
                                                                    {
                                                                        layout: 'form',
                                                                        region: 'center',
                                                                        border: false,
                                                                        items:
                                                                            [
                                                                                {
                                                                                    fieldLabel: 'Número',
                                                                                    xtype: 'textfield',
                                                                                    hiddenName: 'reservista',
                                                                                    name: 'reservista',
                                                                                    enableKeyEvents: true,
                                                                                    width: 140,
                                                                                    style: this.getColorBackgroud(cfg.values.state, cfg.values.reservista_diff)
                                                                                },
                                                                            ]
                                                                    },
                                                                ]
                                                            },
                                                        ]
                                                    },
                                                    {
                                                        xtype: 'fieldset',
                                                        title: 'Conselho Profissional',
                                                        items: [
                                                            {
                                                                layout: 'hbox',
                                                                border: false,
                                                                items: [
                                                                    {
                                                                        layout: 'form',
                                                                        region: 'center',
                                                                        border: false,
                                                                        items:
                                                                            [
                                                                                {
                                                                                    fieldLabel: 'Número',
                                                                                    xtype: 'textfield',
                                                                                    hiddenName: 'professional_council',
                                                                                    name: 'professional_council',
                                                                                    enableKeyEvents: true,
                                                                                    width: 140,
                                                                                    style: this.getColorBackgroud(cfg.values.state, cfg.values.professional_council_diff)
                                                                                },
                                                                            ]
                                                                    },
                                                                    {
                                                                        layout: 'form',
                                                                        region: 'center',
                                                                        border: false,
                                                                        style: 'margin-left: 5px',
                                                                        items:
                                                                            [
                                                                                {
                                                                                    xtype: 'rest-autocompletefield',
                                                                                    fieldLabel: 'UF',
                                                                                    name: 'professional_council_state',
                                                                                    displayField: 'unicode',
                                                                                    allowBlank: true,
                                                                                    rest: 'rh.estado.Restful',
                                                                                    width: 125,
                                                                                    style: this.getColorBackgroud(cfg.values.state, cfg.values.professional_council_state_diff)
                                                                                }
                                                                            ]
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                layout: 'hbox',
                                                                border: false,
                                                                items: [
                                                                    {
                                                                        layout: 'form',
                                                                        region: 'center',
                                                                        border: false,
                                                                        items:
                                                                            [
                                                                                {
                                                                                    name: "professional_council_expedition_date",
                                                                                    fieldLabel: "Data de Expedição",
                                                                                    xtype: "datefield",
                                                                                    allowBlank: true,
                                                                                    width: 140,
                                                                                    style: this.getColorBackgroud(cfg.values.state, cfg.values.professional_council_expedition_date_diff)
                                                                                }
                                                                            ]
                                                                    },
                                                                    {
                                                                        layout: 'form',
                                                                        region: 'center',
                                                                        border: false,
                                                                        style: 'margin-left: 5px',
                                                                        items:
                                                                            [
                                                                                {
                                                                                    name: "professional_council_validity_date",
                                                                                    fieldLabel: "Data de Validade",
                                                                                    xtype: "datefield",
                                                                                    allowBlank: true,
                                                                                    width: 123,
                                                                                    style: this.getColorBackgroud(cfg.values.state, cfg.values.professional_council_validity_date_diff)
                                                                                }
                                                                            ]
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                xtype: 'textfield',
                                                                width: 375,
                                                                enableKeyEvents: true,
                                                                name: 'professional_council_issuer',
                                                                fieldLabel: 'Órgão Emissor',
                                                                style: this.getColorBackgroud(cfg.values.state, cfg.values.professional_council_issuer_diff)
                                                            },
                                                        ]
                                                    },
                                                    {
                                                        xtype: 'fieldset',
                                                        title: 'Título de Eleitor',
                                                        items: [
                                                            {
                                                                xtype: 'textfield',
                                                                width: 375,
                                                                enableKeyEvents: true,
                                                                name: 'titulo_eleitor',
                                                                fieldLabel: 'Número',
                                                                style: this.getColorBackgroud(cfg.values.state, cfg.values.titulo_eleitor_diff)
                                                            },
                                                            {
                                                                layout: 'hbox',
                                                                border: false,
                                                                items: [
                                                                    {
                                                                        layout: 'form',
                                                                        region: 'center',
                                                                        border: false,
                                                                        items:
                                                                            [
                                                                                {
                                                                                    fieldLabel: 'Zona',
                                                                                    xtype: 'textfield',
                                                                                    hiddenName: 'zona_titulo',
                                                                                    name: 'zona_titulo',
                                                                                    enableKeyEvents: true,
                                                                                    width: 140,
                                                                                    style: this.getColorBackgroud(cfg.values.state, cfg.values.zona_titulo_diff)
                                                                                }
                                                                            ]
                                                                    },
                                                                    {
                                                                        layout: 'form',
                                                                        region: 'center',
                                                                        border: false,
                                                                        style: 'margin-left: 5px',
                                                                        items:
                                                                            [
                                                                                {
                                                                                    fieldLabel: 'Seção',
                                                                                    xtype: 'textfield',
                                                                                    hiddenName: 'secao_titulo',
                                                                                    name: 'secao_titulo',
                                                                                    enableKeyEvents: true,
                                                                                    width: 123,
                                                                                    style: this.getColorBackgroud(cfg.values.state, cfg.values.secao_titulo_diff)
                                                                                }
                                                                            ]
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                xtype: 'rest-autocompletefield',
                                                                fieldLabel: 'Cidade de Expedição',
                                                                name: 'municipio_titulo',
                                                                displayField: 'unicode',
                                                                allowBlank: true,
                                                                rest: 'rh.localidade.Restful',
                                                                width: 375,
                                                                style: this.getColorBackgroud(cfg.values.state, cfg.values.municipio_titulo_diff)
                                                            },
                                                        ]
                                                    },
                                                    {
                                                        xtype: 'fieldset',
                                                        title: 'Imigrante',
                                                        items: [
                                                            {
                                                                fieldLabel: 'Tempo de permanência',
                                                                xtype: 'choicefield',
                                                                choiceId: 'rh.IMMIGRANTE_RESIDENCE_TIME',
                                                                hiddenName: 'immigrant_residence_time',
                                                                name: 'immigrant_residence_time',
                                                                width: 148,
                                                                style: this.getColorBackgroud(cfg.values.state, cfg.values.immigrant_residence_time_diff)
                                                            },
                                                            {
                                                                fieldLabel: 'Condição de ingresso',
                                                                xtype: 'choicefield',
                                                                choiceId: 'rh.IMMIGRANTE_ENTRY_CONDITION',
                                                                hiddenName: 'immigrant_entry_condition',
                                                                name: 'immigrant_entry_condition',
                                                                width: 148,
                                                                style: this.getColorBackgroud(cfg.values.state, cfg.values.immigrant_entry_condition_diff)
                                                            }
                                                        ]
                                                    },
                                                ]
                                            },
                                        ]
                                    },
                                    {
                                        region: 'center',
                                        border: false,
                                        width: "400",
                                        style: 'margin-left: 5px',
                                        items: [
                                            {
                                                xtype: 'fieldset',
                                                title: 'Documentos Digitais',
                                                name: 'fieldServidor',
                                                width: "400",
                                                items: [
                                                    this.getFormGed()
                                                ]
                                            },
                                            {
                                                xtype: 'fieldset',
                                                title: 'Foto',
                                                name: 'fieldServidor',
                                                items: [
                                                    {
                                                        layout: 'hbox',
                                                        border: false,
                                                        items: [{
                                                            layout: 'form',
                                                            region: 'center',
                                                            border: false,
                                                            frame: true,
                                                            items: [
                                                                Ext._create('core.fields.ImageFileUploadField', {
                                                                    hideLabel: true,
                                                                    name: 'foto',
                                                                    hideInputDisplay: true,
                                                                    width: 200,
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
                                                        }]
                                                    },
                                                ]
                                            },
                                            {
                                                xtype: 'fieldset',
                                                title: 'Última mensagem de validação',
                                                name: 'fieldServidor',
                                                items: [
                                                    {
                                                        fieldLabel: 'Ultima mensagem de validação',
                                                        hideLabel: true,
                                                        xtype: 'displayfield',
                                                        name: 'last_validation_text'
                                                    },
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            this.tabDependent(cfg),
                            this.tabPendency(cfg),
                        ]
                    }
                ]
            });

        return this._formPanel;
    },

    getTypeStreetChoiceField: function (cfg, values) {
        if (!this._typeStreetChoiceField) {
            this._typeStreetChoiceField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Tipo Logradouro',
                hiddenName: "address_type_street",
                name: "address_type_street",
                choiceId: 'rh.TYPE_STREET',
                allowBlank: false,
                width: 145,
                style: this.getColorBackgroud(values.state, values.address_type_street_diff)
            });
            var store = this._typeStreetChoiceField.getStore();
            var filter = Ext.decode(store.baseParams.filter);
            filter.push({ property: 'value__in', value: [4, 7], stage: -1 });
            store.baseParams.filter = Ext.encode(filter);
            store.load();
        }
        return this._typeStreetChoiceField;
    },

    getMaritalStatusChoiceField: function (cfg_window, cfg) {
        if (!this._maritalStatusChoiceField) {
            this._maritalStatusChoiceField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Estado Civil',
                hiddenName: 'estado_civil',
                name: 'estado_civil',
                width: 148,
                choiceId: 'rh.MARITAL_STATUS',
                style: this.getColorBackgroud(cfg_window.values.state, cfg_window.values.estado_civil_diff)
            });
            var store = this._maritalStatusChoiceField.getStore();
            var filter = Ext.decode(store.baseParams.filter);
            filter.push({ property: 'value__in', value: [6, 7], stage: -1 });
            store.baseParams.filter = Ext.encode(filter);
            store.load();
        }
        return this._maritalStatusChoiceField;
    },
    
    tabDependent: function (cfg) {
        if (!this._tabDependent) {
            this._tabDependent = Ext._create('Ext.Panel', {
                title: 'Dependentes de IR',
                layout: 'border',
                border: false,
                height: 600,
                items: [
                    {
                        region: 'center',
                        border: true,
                        items: [{
                            xtype: 'fieldset',
                            title: 'Dependentes de IR',
                            name: 'fieldServidor',
                            items: [
                                this.getDescription(),
                                this.getDependentGrid(cfg),
                           ]
                        }]
                    }
                ]
            });
        }
        return this._tabDependent;
    },

    getDescription: function() {

        if(!this._description){
            this._description = new Ext.XTemplate(
                '<div style="padding:10px">'+
                    '<ol style="font-weight: bold; font-size:10pt">As atualizações dos dados de dependentes nessa aba são específicas aos de Imposto de Renda visando regularizar informações para o envio do eSocial.</ol>'+
                '</div>'
            );
        }
        return this._description;
    },

    getDependentGrid: function(cfg) {
        if(!this._dependentGrid) {
            this._dependentGrid = Ext._create('rh.registration.forminformation.dependente.DependenteGrid',{
                height: 450,
                width: 950,
            });           
        }
        return this._dependentGrid;
    },

    tabPendency: function (cfg) {
        if (!this._tabPendecy) {
            this._tabPendecy = Ext._create('Ext.Panel', {
                title: 'Pendências',
                layout: 'border',
                border: false,
                height: 500,
                items: [
                    {
                        region: 'center',
                        border: false,
                        items: [{
                            xtype: 'fieldset',
                            title: 'Última mensagem de validação',
                            name: 'fieldServidor',
                            items: [
                                this.getPendencyField()
                            ]
                        }]
                    }
                ]
            });
        }
        return this._tabPendecy;
    },

    getPendencyField: function () {
        if (!this._pendencyField)
            this._pendencyField = Ext._create('Ext.form.DisplayField', {
                fieldLabel: 'Ultima mensagem de validação',
                hideLabel: true,
                name: 'pendency'
            });

        return this._pendencyField;
    },

    getMessageBox: function (message) {
        Ext.Msg.show({
            title: 'Informação',
            icon: Ext.Msg.INFO,
            buttons: Ext.Msg.OK,
            msg: message
        });
    },

    getButtons: function (cfg) {
        if (!this._buttons) {
            this._buttons = [];

            this._buttons.push({
                text: 'Enviar para Validação',
                scope: this,
                iconCls: 'icon-rh icon-core-publication-confirmed',
                handler: function () {
                    this.save(false, true);
                }
            });

            this._buttons.push({
                text: 'Salvar',
                scope: this,
                handler: function () {
                    this.save(true);
                }
            });

            this._buttons.push({
                text: 'Fechar',
                scope: this,
                handler: this.destroy
            });
        }
        return this._buttons;
    },

    getPanelFoto: function (link) {
        if (!this.panelFoto) {
            this.panelFoto = new Ext.Panel({
                id: 'foto-view',
                width: 95,
                height: 120,
            });
        }

        if (link != undefined) {
            this.showHtmlInDisplay(link)
        }

        return this.panelFoto;
    },

    showHtmlInDisplay: function (link) {
        var tpl = new Ext.XTemplate(
            '<div><img src="{link}" alt="Visualização da foto" height="120" width="95"/></div>'
        );

        this.getPanelFoto().removeAll();
        this.getPanelFoto().add(new Ext.Container({
            preventBodyReset: true,
            html: tpl.apply({ link: link })
        }));
        this.getPanelFoto().doLayout();
    },


    getTypeAddressChoiceField: function (cfg, values) {
        if (!this._typeAddressChoiceField) {
            this._typeAddressChoiceField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Tipo Endereço',
                hiddenName: 'address_type_address',
                name: 'address_type_address',
                choiceId: 'rh.TYPE_ADDRESS',
                width: 140,
                style: this.getColorBackgroud(values.state, values.address_type_address_diff)

            });
        }
        return this._typeAddressChoiceField;
    },

    getBloodChoiceField: function (cfg, values) {
        if (!this._bloodChoiceField) {
            this._bloodChoiceField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Sangue',
                hiddenName: 'sangue',
                name: 'sangue',
                choiceId: 'rh.BLOOD',
                width: 100,
                style: this.getColorBackgroud(values.state, values.sangue_diff)
            });
            var store = this._bloodChoiceField.getStore();
            var filter = Ext.decode(store.baseParams.filter);
            filter.push({ property: 'value__in', value: [5], stage: -1 });
            store.baseParams.filter = Ext.encode(filter);
            store.load();
        }
        return this._bloodChoiceField;
    },

    getFactorRhCoiceField: function (cfg, values) {
        if (!this._factorRhChoiceField) {
            this._factorRhChoiceField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Fator RH',
                hiddenName: 'fator_rh',
                choiceId: 'rh.FACTOR_RH',
                name: 'fator_rh',
                width: 100,
                style: this.getColorBackgroud(values.state, values.fator_rh_diff)
            });
            var store = this._factorRhChoiceField.getStore();
            var filter = Ext.decode(store.baseParams.filter);
            filter.push({ property: 'value__in', value: [3], stage: -1 });
            store.baseParams.filter = Ext.encode(filter);
            store.load();
        }
        return this._factorRhChoiceField;
    },

    getOutsiderField: function (cfg, values) {
        if (!this._outsiderField) {
            this._outsiderField = Ext._create('Ext.form.Checkbox', {
                boxLabel: "Endereço no exterior",
                allowBlank: true,
                hideLabel: true,
                name: "address_outsider",
                checked: false,
                fieldLabel: '&nbsp;',
                labelSeparator: '&nbsp;',
                scope: this,
                listeners: {
                    scope: this,
                    check: function (fld, checked) {
                        this._observe();
                    }
                },
                style: this.getColorBackgroud(values.state, values.outsider_diff)
            });
        }
        return this._outsiderField;
    },

    getPhoneOutsiderField: function (cfg, values) {
        if (!this._phone_outsiderField) {
            this._phone_outsiderField = Ext._create('Ext.form.Checkbox', {
                boxLabel: "Telefone no exterior",
                allowBlank: true,
                hideLabel: true,
                name: "phone_outsider",
                checked: false,
                fieldLabel: '&nbsp;',
                labelSeparator: '&nbsp;',
                scope: this,
                listeners: {
                    scope: this,
                    check: function (fld, checked) {
                        if (checked) {
                            this.getPhoneField().hide();
                            this.getPhoneInternationalField().show();
                        } else {
                            this.getPhoneField().show();
                            this.getPhoneInternationalField().hide();
                        }
                    }
                },
            });
        }
        return this._phone_outsiderField;
    },

    getCountyField: function (cfg, values) {
        if (!this._countyField) {
            this._countyField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Cidade',
                name: 'address_city',
                displayField: 'unicode',
                allowBlank: false,
                rest: 'rh.localidade.Restful',
                width: 400,
                style: this.getColorBackgroud(values.state, values.address_city_diff)
            });
        }
        return this._countyField;
    },

    getCountryField: function (cfg, values) {
        if (!this._countryField) {
            this._countryField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: "País(em caso de residência no exterior)",
                allowBlank: true,
                rest: "rh.country.Restful",
                name: "address_country",
                width: 400,
                style: this.getColorBackgroud(values.state, values.address_country_diff)
            });
        }
        return this._countryField;
    },

    getPhoneField: function (cfg, values) {
        if (!this._phone_with_mask) {
            this._phone_with_mask = Ext._create('core.fields.PhoneField', {
                fieldLabel: 'Principal',
                name: (values.phone_outsider == false ? 'phone_main' : ''),
                hiddenName: (values.phone_outsider == false ? 'phone_main' : ''),
                enableKeyEvents: true,
                width: 400,
                hidden: values.phone_outsider,
                style: this.getColorBackgroud(values.state, values.phone_main_diff) + 'padding-right: 10px !important;',
                listeners: {
                    scope: this,
                    beforerender: function (field) {
                        if (typeof field.getFormatedField == 'function') {
                            field.getFormatedField().fieldClass = "x-form-field";
                        }
                    }
                }
            });
        }

        return this._phone_with_mask;
    },

    getContactEmergencyPhoneField: function (cfg, values) {
        if (!this._contactEmergencyPhoneField) {
            this._contactEmergencyPhoneField = Ext._create('core.fields.PhoneField', {
                name: "contact_emergency_phone",
                fieldLabel: "Telefone Emergência",
                allowBlank: true,
                width: 148,
                style: this.getColorBackgroud(values.state, values.contact_emergency_phone_diff),
                listeners: {
                    scope: this,
                    beforerender: function (field) {
                        if (typeof field.getFormatedField == 'function') {
                            field.getFormatedField().fieldClass = "x-form-field";
                        }
                    }
                }
            });
        }

        return this._contactEmergencyPhoneField;
    },

    getPhoneInternationalField: function (cfg, values) {
        if (!this._internationalPhone) {
            this._internationalPhone = Ext._create('Ext.form.TextField', {
                maxLength: 15,
                width: 400,
                enableKeyEvents: true,
                name: (values.phone_outsider == true ? 'phone_main' : ''),
                hiddenName: (values.phone_outsider == true ? 'phone_main' : ''),
                allowDecimals: false,
                allowNegative: false,
                maskRe: /\d/,
                hidden: !values.phone_outsider,
                fieldLabel: 'Telefone (somente numeros)',
                style: this.getColorBackgroud(values.state, values.phone_main_diff)
            });
        }
        return this._internationalPhone;
    },

    getPublicPlaceField: function (cfg, values) {
        if (!this._publicPlaceField) {
            this._publicPlaceField = Ext._create('Ext.form.TextField', {
                maxLength: 100,
                width: 400,
                enableKeyEvents: true,
                name: 'address_public_place',
                fieldLabel: 'Logradouro',
                style: this.getColorBackgroud(values.state, values.address_public_place_diff)
            });
        }
        return this._publicPlaceField;
    },

    getNumberField: function (cfg, values) {
        if (!this._numberField) {
            this._numberField = Ext._create('Ext.form.TextField', {
                maxLength: 12,
                fieldLabel: 'Número',
                xtype: 'textfield',
                hiddenName: 'address_number',
                name: 'address_number',
                enableKeyEvents: true,
                width: 140,
                style: this.getColorBackgroud(values.state, values.address_number_diff)
            });
        }
        return this._numberField;
    },

    getCEPField: function (cfg, values) {
        if (!this._cepField) {
            this._cepField = Ext._create('Ext.form.TextField', {
                maxLength: 10,
                name: 'address_zip_code',
                fieldLabel: "CEP/Código postal",
                xtype: 'cepfield',
                allowBlank: true,
                width: 148,
                style: this.getColorBackgroud(values.state, values.address_zip_code_diff)
            });
        }
        return this._cepField;
    },

    getNeighborhoodField: function (cfg, values) {
        if (!this._neighborhoodField) {
            this._neighborhoodField = Ext._create('Ext.form.TextField', {
                maxLength: 50,
                width: 400,
                enableKeyEvents: true,
                name: 'address_district',
                fieldLabel: 'Bairro/Distrito',
                style: this.getColorBackgroud(values.state, values.address_district_diff)
            });
        }
        return this._neighborhoodField;
    },

    getComplementField: function (cfg, values) {
        if (!this._complementField) {
            this._complementField = Ext._create('Ext.form.TextField', {
                allowBlank: true,
                maxLength: 2000,
                width: 400,
                enableKeyEvents: true,
                name: 'address_complement',
                fieldLabel: 'Complemento',
                style: this.getColorBackgroud(values.state, values.address_complement_diff)
            });
        }
        return this._complementField;
    },

    getOutsiderCittyField: function (cfg, values) {
        if (!this._outsiderCittyField) {
            this._outsiderCittyField = Ext._create('Ext.form.TextField', {
                maxLength: 50,
                allowBlank: true,
                fieldLabel: "Cidade no Exterior",
                name: "address_outsider_citty",
                width: 400,
                style: this.getColorBackgroud(values.state, values.address_outsider_citty_diff)
            });
        }
        return this._outsiderCittyField;
    },

    getNewAddressField: function (cfg, values) {
        if (!this._newAddressField) {
            this._newAddressField = Ext._create('Ext.form.Checkbox', {
                boxLabel: "Endereço Novo ?",
                allowBlank: true,
                hideLabel: true,
                name: "address_new",
                checked: false,
                fieldLabel: '&nbsp;',
                labelSeparator: '&nbsp;',
                scope: this,
                listeners: {
                    scope: this,
                    check: function (fld, checked) {
                        this._observe();
                    }
                },
                style: this.getColorBackgroud(values.state, values.address_new_diff)
            });
        }
        return this._newAddressField;
    },
});

