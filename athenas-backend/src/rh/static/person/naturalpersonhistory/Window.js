Ext._define("rh.person.naturalpersonhistory.Window", {
    extend: "core.RestfulWindow",

    rest: "rh.person.naturalpersonhistory.Restful",

    width: 600,
    height: 650,

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});
        console.info(cfg.values);
        Ext.applyIf(cfg, {
            modal: false,
        });

        rh.person.naturalpersonhistory.Window.superclass.constructor.call(this, cfg);

        console.info(this.values);
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create("Ext.form.FormPanel", {
                border: false,
                frame: true,
                labelWidth: 200,
                items: [
                    {
                        name: "natural_person",
                        fieldLabel: "Pessoa Física",
                        xtype: "rest-autocompletefield",
                        allowBlank: true,
                        rest: "rh.person.naturalperson.Restful",
                    },
                    {
                        name: "when",
                        fieldLabel: "Quando",
                        xtype: "datefield",
                        allowBlank: false,
                        width: 465,
                    },
                    {
                        name: "send_esocial",
                        fieldLabel: "Enviar para eSocial",
                        xtype: "checkbox",
                        allowBlank: true,
                    },
                    this.getTabPanel(),
                ],
            });
        return this._formPanel;
    },

    getTabPanel: function (cfg) {
        if (!this._tabPanel)
            this._tabPanel = Ext._create("Ext.TabPanel", {
                height: 494,
                border: false,
                activeTab: 0,
                deferredRender: false,
                items: [
                    this.getPersonalDataTab(),
                    this.getPersonalDocumentsTab(),
                    this.getAddressTab(),
                    this.getPhoneTab(),
                ],
            });

        return this._tabPanel;
    },

    getAddressTab: function (cfg) {
        if (!this._addressTab)
            this._addressTab = Ext._create("Ext.Panel", {
                title: "Endereço",
                layout: {
                    type: "vbox",
                    align: "stretch",
                },
                frame: true,
                border: false,
                items: [
                    {
                        xtype: "panel",
                        layout: "form",
                        height: 460,
                        labelWidth: 200,
                        items: [
                            {
                                name: "tipo_endereco",
                                hiddenName: "tipo_endereco",
                                fieldLabel: "Tipo do Endere\u00e7o",
                                xtype: "choicefield",
                                choiceId: "rh.TYPE_ADDRESS",
                                width: 350,
                                allowBlank: true,
                            },
                            {
                                name: "tipo_logradouro",
                                fieldLabel: "Tipo do Logradouro",
                                xtype: "choicefield",
                                allowBlank: true,
                                hiddenName: "tipo_logradouro",
                                choiceId: "rh.TYPE_STREET",
                                width: 350,
                            },
                            Ext._create("core.fields.AutocompleteField", {
                                name: "municipio",
                                fieldLabel: "Cidade",
                                allowBlank: true,
                                rest: "rh.localidade.Restful",
                            }),
                            {
                                name: "logradouro",
                                fieldLabel: "Logradouro",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 100,
                            },
                            {
                                name: "bairro",
                                fieldLabel: "Bairro",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 50,
                            },
                            {
                                name: "cep",
                                fieldLabel: "CEP",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 10,
                            },
                            {
                                name: "numero",
                                fieldLabel: "N\u00famero",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 12,
                            },
                            {
                                name: "complemento",
                                fieldLabel: "Complemento",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 2000,
                            },
                            {
                                name: "outsider",
                                fieldLabel: "Endere\u00e7o no exterior",
                                xtype: "checkbox",
                                allowBlank: true,
                            },
                            {
                                name: "country",
                                fieldLabel: "Pa\u00eds(Residentes no Exterior)",
                                xtype: "rest-autocompletefield",
                                allowBlank: true,
                                rest: "rh.country.Restful",
                            },
                            {
                                name: "outsider_citty",
                                fieldLabel: "Cidade no Exterior",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 50,
                            },
                        ],
                    },
                ],
            });
        return this._addressTab;
    },

    getPhoneTab: function (cfg) {
        if (!this._phoneTab)
            this._phoneTab = Ext._create("Ext.Panel", {
                title: "Telefone(s)",
                layout: {
                    type: "vbox",
                    align: "stretch",
                },
                frame: true,
                border: false,
                items: [
                    {
                        xtype: "panel",
                        layout: "form",
                        height: 400,
                        labelWidth: 200,
                        defaults: {
                            width: 350,
                        },
                        items: [
                            {
                                name: "phone_main",
                                fieldLabel: "Telefone Principal",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 15,
                            },
                            {
                                xtype: "choicefield",
                                fieldLabel: "Tipo telefone",
                                name: "phone_type",
                                hiddenName: "phone_type",
                                choiceId: "rh.TYPE_PHONE",
                            },
                            {
                                name: "phone_public",
                                fieldLabel: "Telefone Público",
                                xtype: "checkbox",
                                allowBlank: true,
                            },
                            {
                                name: "phone_description",
                                fieldLabel: "Descri\u00e7\u00e3o",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 80,
                            },
                            {
                                name: "phone_contact_emergency",
                                fieldLabel: "Telefone de Emerg\u00eancia",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 15,
                            },
                            {
                                name: "contact_emergency_name",
                                fieldLabel: "Nome do Contato de Emerg\u00eancia",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 100,
                            },
                        ],
                    },
                ],
            });
        return this._phoneTab;
    },

    getPersonalDataTab: function (cfg) {
        if (!this._personalDataTab)
            this._personalDataTab = Ext._create("Ext.Panel", {
                title: "Dados pessoais.",
                layout: {
                    type: "vbox",
                    align: "stretch",
                },
                frame: true,
                border: false,
                autoScroll: true,
                items: [
                    {
                        xtype: "panel",
                        layout: "form",
                        labelWidth: 160,
                        height: 560,
                        autoScroll: true,
                        defaults: {
                            width: 370,
                        },
                        items: [
                            {
                                name: "nome",
                                fieldLabel: "Nome",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 100,
                            },
                            {
                                name: "social_name",
                                fieldLabel: "Nome Social",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 100,
                            },
                            {
                                name: "nome_conjuge",
                                fieldLabel: "Nome C\u00f4njuge",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 80,
                            },
                            {
                                name: "nome_mae",
                                fieldLabel: "Nome M\u00e3e",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 80,
                            },
                            {
                                name: "nome_pai",
                                fieldLabel: "Nome Pai",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 80,
                            },
                            {
                                name: "genero",
                                fieldLabel: "G\u00eanero",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 100,
                            },
                            {
                                fieldLabel: "Raça/Cor",
                                xtype: "choicefield",
                                hiddenName: "raca_cor",
                                name: "raca_cor",
                                choiceId: "rh.TYPE_RACE",
                            },
                            {
                                hiddenName: "sangue",
                                name: "sangue",
                                fieldLabel: "Sangue",
                                xtype: "choicefield",
                                choiceId: "rh.BLOOD",
                            },
                            {
                                hiddenName: "sexo",
                                fieldLabel: "Sexo",
                                xtype: "combo",
                                allowBlank: false,
                                validateOnBlur: true,
                                blankText: "É necessário preencher este campo.",
                                store: rh.employee.specialized.CHOICES.SEXO,
                                displayField: "description",
                                typeAhead: true,
                                mode: "local",
                                triggerAction: "all",
                                emptyText: "Selecione um item...",
                            },
                            {
                                fieldLabel: "Orientação Sexual",
                                xtype: "choicefield",
                                hiddenName: "sexual_orientation",
                                name: "sexual_orientation",
                                choiceId: "rh.SEXUAL_ORIENTATION",
                            },
                            {
                                name: "necessidade_especial",
                                fieldLabel: "Necessidade Especial",
                                xtype: "checkbox",
                                allowBlank: true,
                            },
                            {
                                name: "profissao",
                                fieldLabel: "Profiss\u00e3o",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 100,
                            },
                            {
                                name: "renda_familiar",
                                fieldLabel: "Renda Familiar",
                                xtype: "numberfield",
                                allowBlank: true,
                                allowDecimals: true,
                                decimalPrecision: 2,
                            },
                            {
                                name: "has_serious_diseases",
                                fieldLabel: "Doença Grave",
                                xtype: "checkbox",
                                allowBlank: true,
                            },
                            {
                                name: "retired",
                                fieldLabel: "Aposentado",
                                xtype: "checkbox",
                                allowBlank: true,
                            },
                            {
                                name: "is_lawyer",
                                fieldLabel: "Advogado",
                                xtype: "checkbox",
                                allowBlank: true,
                            },
                            {
                                name: "oab",
                                fieldLabel: "OAB",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 20,
                            },
                            {
                                name: "name_cache",
                                fieldLabel: "Cache Name",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 100,
                            },
                            {
                                name: "slug",
                                fieldLabel: "Slug",
                                xtype: "textfield",
                                allowBlank: true,
                            },
                            {
                                name: "email",
                                fieldLabel: "Email",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 254,
                            },
                            {
                                name: "enable_protocol",
                                fieldLabel: "Habilitar protocolo",
                                xtype: "checkbox",
                                allowBlank: true,
                            },
                            {
                                name: "kind",
                                fieldLabel: "Tipo",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 32,
                            },
                            {
                                name: "rate_fill",
                                fieldLabel: "Rate Fill",
                                xtype: "numberfield",
                                allowBlank: true,
                                allowDecimals: true,
                                decimalPrecision: 2,
                            },
                            {
                                name: "data_nascimento",
                                fieldLabel: "Data de Nascimento",
                                xtype: "datefield",
                                allowBlank: true,
                            },
                            {
                                name: "data_obito",
                                fieldLabel: "Data \u00d3bito",
                                xtype: "datefield",
                                allowBlank: true,
                            },
                            {
                                name: "doador",
                                fieldLabel: "Doador de \u00f3rg\u00e3os",
                                xtype: "checkbox",
                                allowBlank: true,
                            },
                            {
                                name: "uniao_estavel",
                                fieldLabel: "Uni\u00e3o Est\u00e1vel",
                                xtype: "checkbox",
                                allowBlank: true,
                            },
                            {
                                name: "email_pessoal",
                                fieldLabel: "E-mail Pessoal",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 60,
                            },
                            {
                                fieldLabel: "Estado civil",
                                hiddenName: "estado_civil",
                                name: "estado_civil",
                                choiceId: "rh.MARITAL_STATUS",
                                xtype: "choicefield",
                            },
                            {
                                hiddenName: "fator_rh",
                                name: "fator_rh",
                                fieldLabel: "Fator RH",
                                xtype: "choicefield",
                                choiceId: "rh.FACTOR_RH",
                            },
                            {
                                name: "foto",
                                fieldLabel: "Foto",
                                xtype: "ged-imageuploadfield",
                                types: ["image/jpeg", "image/png"],
                                allowBlank: true,
                                validateOnBlur: true,
                                // value: pessoa_fisica.foto,
                                scope: this,
                            },
                            {
                                fieldLabel: "Grau Instrução",
                                hiddenName: "grau_instrucao",
                                name: "grau_instrucao",
                                choiceId: "rh.DEGREE_EDUCATION",
                                xtype: "choicefield",
                            },
                            {
                                name: "municipio_naturalidade",
                                fieldLabel: "Naturalidade",
                                xtype: "rest-autocompletefield",
                                allowBlank: true,
                                rest: "rh.localidade.Restful",
                            },
                            {
                                name: "nationality",
                                fieldLabel: "Nacionalidade",
                                xtype: "rest-autocompletefield",
                                allowBlank: true,
                                rest: "rh.country.Restful",
                            },
                            {
                                name: "nationality_birth",
                                fieldLabel: "Pa\u00eds de nascimento",
                                xtype: "rest-autocompletefield",
                                allowBlank: true,
                                rest: "rh.country.Restful",
                            },
                            {
                                xtype: "choicefield",
                                fieldLabel: "Imigrante tempo de residência",
                                hiddenName: "immigrant_residence_time",
                                choiceId: "rh.IMMIGRANTE_RESIDENCE_TIME",
                            },
                            {
                                xtype: "choicefield",
                                fieldLabel: "Imigrante condição de ingresso",
                                hiddenName: "immigrant_entry_condition",
                                choiceId: "rh.IMMIGRANTE_ENTRY_CONDITION",
                            },
                        ],
                    },
                ],
            });
        return this._personalDataTab;
    },

    getPersonalDocumentsTab: function (cfg) {
        if (!this._personalDocuments)
            this._personalDocuments = Ext._create("Ext.Panel", {
                title: "Documentos pessoais",
                layout: {
                    type: "vbox",
                    align: "stretch",
                },
                frame: true,
                border: false,
                autoScroll: true,
                items: [
                    {
                        xtype: "panel",
                        layout: "form",
                        labelWidth: 160,
                        height: 560,
                        autoScroll: true,
                        items: [
                            {
                                name: "cpf",
                                fieldLabel: "CPF",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 14,
                                width: 370,
                            },

                            {
                                name: "rg",
                                fieldLabel: "RG",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 30,
                                width: 370,
                            },
                            {
                                name: "rg_data_expedicao",
                                fieldLabel: "RG - Data da Expedi\u00e7\u00e3o",
                                xtype: "datefield",
                                allowBlank: true,
                                width: 370,
                            },
                            {
                                name: "rg_orgao",
                                fieldLabel: "RG - Org\u00e3o",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 30,
                                width: 370,
                            },
                            {
                                name: "rg_uf",
                                fieldLabel: "RG - UF",
                                xtype: "rest-autocompletefield",
                                allowBlank: true,
                                rest: "rh.estado.Restful",
                            },
                            {
                                name: "cnh",
                                fieldLabel: "CNH",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 11,
                                width: 370,
                            },
                            {
                                name: "cnh_categoria",
                                fieldLabel: "CNH - Categoria",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 30,
                                width: 370,
                            },
                            {
                                name: "cnh_expedition_date",
                                fieldLabel: "CNH - Data da Expedi\u00e7\u00e3o",
                                xtype: "datefield",
                                allowBlank: true,
                                width: 370,
                            },
                            {
                                name: "cnh_first_date",
                                fieldLabel: "CNH - Data da primeira habilita\u00e7\u00e3o",
                                xtype: "datefield",
                                allowBlank: true,
                                width: 370,
                            },
                            {
                                name: "cnh_state",
                                fieldLabel: "CNH - Estado",
                                xtype: "rest-autocompletefield",
                                allowBlank: true,
                                rest: "rh.estado.Restful",
                            },
                            {
                                name: "cnh_validity_date",
                                fieldLabel: "CNH - Data de Validade",
                                xtype: "datefield",
                                allowBlank: true,
                                width: 370,
                            },
                            {
                                name: "professional_council",
                                fieldLabel: "Conselho Profissional",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 30,
                                width: 370,
                            },
                            {
                                name: "professional_council_state",
                                fieldLabel: "Conselho Profissional - Estado",
                                xtype: "rest-autocompletefield",
                                allowBlank: true,
                                rest: "rh.estado.Restful",
                            },
                            {
                                name: "professional_council_expedition_date",
                                fieldLabel: "Conselho Profissional - Data da Expedi\u00e7\u00e3o",
                                xtype: "datefield",
                                allowBlank: true,
                                width: 370,
                            },
                            {
                                name: "professional_council_validity_date",
                                fieldLabel: "Conselho Profissional - Data de Validade",
                                xtype: "datefield",
                                allowBlank: true,
                                width: 370,
                            },
                            {
                                name: "professional_council_issuer",
                                fieldLabel: "Conselho Profissional - Org\u00e3o de Expedi\u00e7\u00e3o",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 256,
                                width: 370,
                            },
                            {
                                name: "nis",
                                fieldLabel: "NIS",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 30,
                                width: 370,
                            },
                            {
                                name: "reservista",
                                fieldLabel: "Reservista",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 30,
                                width: 370,
                            },
                            {
                                name: "classe_reservista",
                                fieldLabel: "Reservista - Classe",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 30,
                                width: 370,
                            },
                            {
                                name: "ric",
                                fieldLabel: "RIC",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 30,
                                width: 370,
                            },
                            {
                                name: "ric_expedition_date",
                                fieldLabel: "RIC - Data da Expedi\u00e7\u00e3o",
                                xtype: "datefield",
                                allowBlank: true,
                                width: 370,
                            },
                            {
                                name: "ric_issuer",
                                fieldLabel: "RIC - Org\u00e3o Emissor",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 256,
                                width: 370,
                            },
                            {
                                name: "ric_state",
                                fieldLabel: "RIC - Estado",
                                xtype: "rest-autocompletefield",
                                allowBlank: true,
                                rest: "rh.estado.Restful",
                            },
                            {
                                name: "rne",
                                fieldLabel: "RNE",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 30,
                                width: 370,
                            },
                            {
                                name: "rne_expedition_date",
                                fieldLabel: "RNE - Data da Expedi\u00e7\u00e3o",
                                xtype: "datefield",
                                allowBlank: true,
                                width: 370,
                            },
                            {
                                name: "rne_issuer",
                                fieldLabel: "RNE - Org\u00e3o Emissor",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 256,
                                width: 370,
                            },
                            {
                                name: "rne_state",
                                fieldLabel: "RNE - Estado",
                                xtype: "rest-autocompletefield",
                                allowBlank: true,
                                rest: "rh.estado.Restful",
                            },
                            {
                                name: "titulo_eleitor",
                                fieldLabel: "T\u00edtulo Eleitor",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 30,
                                width: 370,
                            },
                            {
                                name: "municipio_titulo",
                                fieldLabel: "T\u00edtulo de Eleitor - Municipio",
                                xtype: "rest-autocompletefield",
                                allowBlank: true,
                                rest: "rh.localidade.Restful",
                            },
                            {
                                name: "secao_titulo",
                                fieldLabel: "T\u00edtulo de Eleitor - Se\u00e7\u00e3o",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 30,
                                width: 370,
                            },
                            {
                                name: "zona_titulo",
                                fieldLabel: "T\u00edtulo de Eleitor - Zona",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 30,
                                width: 370,
                            },
                            {
                                name: "ctps",
                                fieldLabel: "CTPS",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 30,
                                width: 370,
                            },
                            {
                                name: "ctps_state",
                                fieldLabel: "CTPS - Estado",
                                xtype: "rest-autocompletefield",
                                allowBlank: true,
                                rest: "rh.estado.Restful",
                            },
                            {
                                name: "serie_ctps",
                                fieldLabel: "CTPS - S\u00e9rie",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 30,
                                width: 370,
                            },
                            {
                                name: "pis_pasep",
                                fieldLabel: "PIS/PASEP",
                                xtype: "textfield",
                                allowBlank: true,
                                maxLength: 30,
                                width: 370,
                            },
                        ],
                    },
                ],
            });
        return this._personalDocuments;
    },
});
