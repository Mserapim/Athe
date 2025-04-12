rh.employee.specialized.tab.fields.NaturalPerson = Ext.extend(rh.employee.specialized.tab.fields.Field, {
    constructor: function (cfg) {
        rh.employee.specialized.tab.fields.NaturalPerson.superclass.constructor.call(this, cfg);
    },

    fields: function () {
        var column1_items = [];
        var column2_items = [];
        column1_items.push({
            name: 'employeePk',
            xtype: 'hidden',
        });
        column1_items.push({
            name: 'naturalPersonPk',
            xtype: 'hidden',
        });
        column1_items.push(this.getCpfField({}));

        column1_items.push({
            width: '90%',
            name: 'social_name',
            fieldLabel: 'Nome social *',
            xtype: 'textfield',
            allowBlank: false,
            validateOnBlur: true,
            blankText: 'É necessário preencher este campo.',
        });

        column1_items.push({
            width: '90%',
            name: 'nome',
            fieldLabel: 'Nome registral *',
            xtype: 'textfield',
            allowBlank: false,
            validateOnBlur: true,
            blankText: 'É necessário preencher este campo.',
        });

        var f1 = Ext._create('Ext.Panel', {
            layout: 'column',
            items: [
                {
                    columnWidth: '.50',
                    layout: 'form',
                    items: [
                        {
                            width: '100%',
                            name: 'sexo',
                            hiddenName: 'sexo',
                            fieldLabel: 'Sexo',
                            xtype: 'combo',
                            allowBlank: false,
                            validateOnBlur: true,
                            blankText: 'É necessário preencher este campo.',
                            store: rh.employee.specialized.CHOICES.SEXO,
                            displayField: 'description',
                            typeAhead: true,
                            mode: 'local',
                            triggerAction: 'all',
                            emptyText: 'Selecione um item...',
                            selectOnFocus: true,
                            editable: true,
                        },
                    ],
                },
                {
                    columnWidth: '.50',
                    layout: 'form',
                    items: [{
                        width: '100%',
                        fieldLabel: 'Raça/Cor *',
                        xtype: 'choicefield',
                        hiddenName: 'raca_cor',
                        name: 'raca_cor',
                        choiceId: 'rh.TYPE_RACE',
                        allowBlank: false,
                        blankText: 'É necessário preencher o campo Raça/Cor.',
                    }]
                }]
            });
            column1_items.push(f1);

        var f1 = Ext._create('Ext.Panel', {
            layout: 'column',
            items: [
                {
                    columnWidth: '.50',
                    layout: 'form',
                    items: [{
                        fieldLabel: 'Orientação Sexual *',
                        xtype: 'choicefield',
                        hiddenName: 'sexual_orientation',
                        name: 'sexual_orientation',
                        choiceId: 'rh.SEXUAL_ORIENTATION',
                        allowBlank: false,
                        width: '95%',
                    }]
                },
                {
                    columnWidth: ".50",
                    layout: "form",
                    items: [
                        {
                            width: 200,
                            xtype: 'textfield',
                            fieldLabel: 'Identidade de Gênero',
                            allowBlank: true,
                            name: 'genero',
                            hiddenName: 'genero',
                        },
                    ],
                },
            ],
        });
        column1_items.push(f1);

        column1_items.push(this.getCivilStatusField({ value: 1 }));

        f1 = Ext._create('Ext.Panel', {
            layout: 'column',
            items: [
                {
                    columnWidth: '.60',
                    layout: 'form',
                    items: [{
                        width: '100%',
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Naturalidade *',
                        name: 'municipio_naturalidade',
                        displayField: 'unicode',
                        allowBlank: false,
                        rest: 'rh.localidade.Restful',
                        blankText: 'É necessário preencher o campo Naturalidade.',
                    }]
                }]
            });
            column1_items.push(f1);

        f1 = Ext._create('Ext.Panel', {
            layout: 'column',
            items: [
                {
                    columnWidth: '.60',
                    layout: 'form',
                    items: [{
                        width: '100%',
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Nacionalidade *',
                        name: 'nationality',
                        displayField: 'unicode',
                        allowBlank: false,
                        rest: 'rh.country.Restful',
                        blankText: 'É necessário preencher o campo Nacionalidade.',
                    }]
                }]
            });
            column1_items.push(f1);

        f1 = Ext._create('Ext.Panel', {
            layout: 'column',
            items: [
                {
                    columnWidth: '.60',
                    layout: 'form',
                    items: [{
                        width: '100%',
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'País de nascimento *',
                        name: 'nationality_birth',
                        displayField: 'unicode',
                        allowBlank: true,
                        rest: 'rh.country.Restful'
                    }]
                }]
            });
            column1_items.push(f1);

            column1_items.push({
                width: '90%',
                name: 'email_institucional',
                fieldLabel: 'Email institucional',
                xtype: 'textfield',
                allowBlank: true,
            });
            column1_items.push({
                width: '90%',
                name: 'email_pessoal',
                fieldLabel: 'Email pessoal',
                xtype: 'textfield',
                allowBlank: true,
            });

            f1 = Ext._create('Ext.Panel', {
                layout: 'column',
                items: [{
                    columnWidth: '.50',
                    layout: 'form',
                    items: [{
                        name: 'data_nascimento',
                        fieldLabel: 'Data nascimento *',
                        xtype: 'datefield',
                        allowBlank: false,
                        validateOnBlur: true,
                        blankText: 'É necessário preencher o campo Data nascimento.'
                    }]
                },
                {
                    columnWidth: '.50',
                    layout: 'form',
                    items: [{
                        name: 'data_obito',
                        fieldLabel: 'Data Óbito',
                        xtype: 'datefield',
                        allowBlank: true,
                    }]
                }]
            });
            column1_items.push(f1);

        f1 = Ext._create('Ext.Panel', {
            layout: 'column',
            items: [
                {
                    columnWidth: '.33',
                    layout: 'form',
                    items: [{
                        width: 100,
                        hiddenName: 'sangue',
                        name: 'sangue',
                        fieldLabel: 'Sangue *',
                        xtype: 'choicefield',
                        choiceId: 'rh.BLOOD',
                        allowBlank: false,
                        blankText: 'É necessário preencher o campo Sangue.',
                    }]
                },
                {
                    columnWidth: '.33',
                    layout: 'form',
                    items: [{
                        width: 100,
                        hiddenName: 'fator_rh',
                        name: 'fator_rh',
                        fieldLabel: 'Fator RH *',
                        xtype: 'choicefield',
                        choiceId: 'rh.FACTOR_RH',
                        allowBlank: false,
                        blankText: 'É necessário preencher o campo Fator RH.',
                    }]
                },
                {
                    columnWidth: '.33',
                    layout: 'form',
                    items: [{
                        width: '100%',
                        name: 'doador',
                        fieldLabel: 'Doador',
                        xtype: 'checkbox',
                        allowBlank: true,
                    }]
                }]
            });
            column2_items.push(f1);

        column2_items.push({
            width: '90%',
            name: 'nome_pai',
            fieldLabel: 'Nome Pai',
            xtype: 'textfield',
            allowBlank: true,
            validateOnBlur: true,
            blankText: 'É necessário preencher este campo.',
        });
        column2_items.push({
            width: '90%',
            name: 'nome_mae',
            fieldLabel: 'Nome Mãe',
            xtype: 'textfield',
            allowBlank: true,
            validateOnBlur: true,
            blankText: 'É necessário preencher este campo.',
        });
        column2_items.push({
            width: '90%',
            name: 'nome_conjuge',
            fieldLabel: 'Nome Cônjuge',
            xtype: 'textfield',
            allowBlank: true,
            validateOnBlur: true,
            blankText: 'É necessário preencher este campo.',
        });
        column2_items.push({
            xtype: 'choicefield',
            fieldLabel: 'Imigrante tempo de residência',
            hiddenName: 'immigrant_residence_time',
            choiceId: 'rh.IMMIGRANTE_RESIDENCE_TIME',
            value: 10,
            width: 580,
            allowBlank: false,
        });
        column2_items.push({
            xtype: 'choicefield',
            fieldLabel: 'Imigrante condição de ingresso',
            hiddenName: 'immigrant_entry_condition',
            choiceId: 'rh.IMMIGRANTE_ENTRY_CONDITION',
            value: 10,
            width: 580,
            allowBlank: false,
        });
        column2_items.push({
            xtype: 'choicefield',
            fieldLabel: 'Regime de cotas',
            hiddenName: 'quota_system',
            choiceId: 'rh.QUOTA_SYSTEM_TYPE',
            value: 1,
            width: 580,
            allowBlank: false,
        });
        column1_items.push({
            width: '90%',
            name: 'rg',
            fieldLabel: 'RG',
            xtype: 'textfield',
            allowBlank: false,
            validateOnBlur: true,
            blankText: 'É necessário preencher este campo.',
        });

            f1 = Ext._create('Ext.Panel', {
                layout: 'column',
                items: [{
                    columnWidth: '.50',
                    layout: 'form',
                    items: [{
                        autoWidth: true,
                        name: 'rg_orgao',
                        fieldLabel: 'RG Órgão *',
                        xtype: 'textfield',
                        allowBlank: false,
                        validateOnBlur: true,
                        blankText: 'É necessário preencher o campo RG Órgão.'
                    }]
                },
                {
                    columnWidth: '.50',
                    layout: 'form',
                    items: [{
                        name: 'rg_data_expedicao',
                        fieldLabel: 'RG Data Expedição *',
                        xtype: 'datefield',
                        allowBlank: false,
                        validateOnBlur: true,
                        blankText: 'É necessário preencher o campo RG Data Expedição.'
                    }]
                }]
            });
            column1_items.push(f1);

        f1 = Ext._create('Ext.Panel', {
            layout: 'column',
            items: [
                {
                    columnWidth: '.50',
                    layout: 'form',
                    items: [{
                        width: '100%',
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'RG - UF *',
                        name: 'rg_uf',
                        displayField: 'unicode',
                        allowBlank: false,
                        rest: 'rh.estado.Restful',
                        blankText: 'É necessário preencher o campo RG - UF.'
                    }]
                }]
            });
            column1_items.push(f1);

            f1 = Ext._create('Ext.Panel', {
                layout: 'column',
                scope: this,
                items: [{
                    columnWidth: '.50',
                    layout: 'form',
                    scope: this,
                    items: [
                        {
                            layout: "form",
                            width: 380,
                            items: [
                                {
                                    xtype: "panel",
                                    title: "Foto",
                                    frame: true,
                                    border: false,
                                    width: 195,
                                    autoHeight: true,
                                    items: [this.getFotoField()],
                                },
                            ],
                        },
                    ],
                },
            ],
        });
        column2_items.push(f1);

        f1 = Ext._create('Ext.Panel', {
            layout: 'column',
            items: [
                {
                    columnWidth: '.50',
                    layout: 'form',
                    items: [
                        {
                            autoWidth: true,
                            name: 'cnh',
                            fieldLabel: 'CNH',
                            xtype: 'textfield',
                            allowBlank: true,
                            validateOnBlur: true,
                            blankText: 'É necessário preencher este campo.',
                        },
                    ],
                },
                {
                    columnWidth: '.50',
                    layout: 'form',
                    items: [{
                        autoWidth: true,
                        name: 'cnh_categoria',
                        fieldLabel: 'CNH - Categoria',
                        xtype: 'textfield',
                        allowBlank: true,
                    }]
                }]
            });
            column1_items.push(f1);

        f1 = Ext._create('Ext.Panel', {
            layout: 'column',
            items: [
                {
                    columnWidth: '.50',
                    layout: 'form',
                    items: [{
                        autoWidth: true,
                        name: 'cnh_expedition_date',
                        fieldLabel: 'CNH - Data Expedição',
                        xtype: 'datefield',
                        allowBlank: true,
                    }]
                },
                {
                    columnWidth: '.50',
                    layout: 'form',
                    items: [{
                        autoWidth: true,
                        name: 'cnh_validity_date',
                        fieldLabel: 'CNH - Data Validate',
                        xtype: 'datefield',
                        allowBlank: true,
                    }]
                }]
            });
            column1_items.push(f1);

        f1 = Ext._create('Ext.Panel', {
            layout: 'column',
            items: [
                {
                    columnWidth: '.50',
                    layout: 'form',
                    items: [{
                        autoWidth: true,
                        name: 'cnh_first_date',
                        fieldLabel: 'CNH - Data Primeira Habilitação',
                        xtype: 'datefield',
                        allowBlank: true,
                    }]
                },
                {
                    columnWidth: '.50',
                    layout: 'form',
                    items: [{
                        width: 230,
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'CNH - UF',
                        name: 'cnh_state',
                        hiddenName: 'cnh_state',
                        name: 'cnh_state',
                        displayField: 'unicode',
                        allowBlank: true,
                        rest: 'rh.estado.Restful'

                    }]
                }]
            });
            column1_items.push(f1);

        f1 = Ext._create('Ext.Panel', {
            layout: 'column',
            items: [
                {
                    columnWidth: '.50',
                    layout: 'form',
                    items: [{
                        autoWidth: true,
                        name: 'ctps',
                        fieldLabel: 'CTPS',
                        xtype: 'textfield',
                        allowBlank: true,
                    }]
                },
                {
                    columnWidth: '.50',
                    layout: 'form',
                    items: [{
                        autoWidth: true,
                        name: 'serie_ctps',
                        fieldLabel: 'Série  de CTPS',
                        xtype: 'textfield',
                        allowBlank: true,
                    }]
                }]
            });
            column1_items.push(f1);

        f1 = Ext._create('Ext.Panel', {
            layout: 'column',
            items: [
                {
                    columnWidth: '.50',
                    layout: 'form',
                    items: [{
                        width: '100%',
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'CTPS - UF',
                        name: 'ctps_state',
                        displayField: 'unicode',
                        allowBlank: true,
                        rest: 'rh.estado.Restful'
                    }]
                }]
            });
            column1_items.push(f1);

            column1_items.push({
                width: '90%',
                name: 'pis_pasep',
                fieldLabel: 'PIS/PASEP *',
                xtype: 'numberfield',
                allowBlank: false,
            });

            f1 = Ext._create('Ext.Panel', {
                layout: 'column',
                items: [{
                    columnWidth: '.50',
                    layout: 'form',
                    items: [{
                        autoWidth: true,
                        name: 'reservista',
                        fieldLabel: 'Reservista',
                        xtype: 'textfield',
                        allowBlank: true,
                    }]
                },
                {
                    columnWidth: '.50',
                    layout: 'form',
                    items: [{
                        autoWidth: true,
                        name: 'classe_reservista',
                        fieldLabel: 'Classe de Reservista',
                        xtype: 'textfield',
                        allowBlank: true,
                    }]
                }]
            });
            column1_items.push(f1);

        f1 = Ext._create('Ext.Panel', {
            layout: 'column',
            items: [
                {
                    columnWidth: '.50',
                    layout: 'form',
                    items: [
                        {
                            autoCreate: { tag: 'input', maxlength: '30' },
                            width: '90%',
                            name: 'professional_council',
                            fieldLabel: 'Conselho Profissional - Número',
                            xtype: 'textfield',
                            allowBlank: true,
                            validateOnBlur: true,
                            blankText: 'É necessário preencher este campo.',
                        },
                    ],
                },
                {
                    columnWidth: '.50',
                    layout: 'form',
                    items: [
                        {
                            width: 230,
                            xtype: 'rest-autocompletefield',
                            fieldLabel: 'Conselho Profissional - UF',
                            name: 'professional_council_state',
                            displayField: 'unicode',
                            allowBlank: true,
                            rest: 'rh.estado.Restful',
                        },
                    ],
                },
            ],
        });
        column1_items.push(f1);

        f1 = Ext._create('Ext.Panel', {
            layout: 'column',
            items: [
                {
                    columnWidth: '.50',
                    layout: 'form',
                    items: [
                        {
                            name: 'professional_council_expedition_date',
                            fieldLabel: 'Conselho Profissional - Data de Expedição',
                            xtype: 'datefield',
                            allowBlank: true,
                            validateOnBlur: true,
                            blankText: '',
                        },
                    ],
                },
                {
                    columnWidth: '.50',
                    layout: 'form',
                    items: [{
                        name: 'professional_council_validity_date',
                        fieldLabel: 'Conselho Profissional - Data de Validate',
                        xtype: 'datefield',
                        allowBlank: true,

                    }]
                }]
            });
            column1_items.push(f1);

            column1_items.push({
                autoCreate: { tag: 'input', maxlength: '30' },
                width: '90%',
                name: 'professional_council_issuer',
                fieldLabel: 'Conselho Profissional - Órgão Emissor',
                xtype: 'textfield',
                allowBlank: true,
            });

            column1_items.push({
                width: '90%',
                name: 'titulo_eleitor',
                fieldLabel: 'Título de Eleitor *',
                xtype: 'textfield',
                allowBlank: false,
                validateOnBlur: true,
                blankText: 'É necessário preencher o campo Título de Eleitor.',
            });

            f1 = Ext._create('Ext.Panel', {
                layout: 'column',
                items: [{
                    columnWidth: '.50',
                    layout: 'form',
                    items: [{
                        autoWidth: true,
                        name: 'zona_titulo',
                        fieldLabel: 'Zona de Título *',
                        xtype: 'textfield',
                        allowBlank: false,
                        validateOnBlur: true,
                        blankText: 'É necessário preencher o campo Zona de Título.',
                    }]
                },
                {
                    columnWidth: '.50',
                    layout: 'form',
                    items: [{
                        autoWidth: true,
                        name: 'secao_titulo',
                        fieldLabel: 'Seção de Título *',
                        xtype: 'textfield',
                        allowBlank: false,
                        validateOnBlur: true,
                        blankText: 'É necessário preencher o campo Seção de Título.',
                    }]
                }]
            });
            column1_items.push(f1);

            column1_items.push({
                width: 350,
                xtype: 'rest-autocompletefield',
                fieldLabel: 'Cidade de Expedição de Título *',
                name: 'municipio_titulo',
                displayField: 'unicode',
                allowBlank: false,
                rest: 'rh.localidade.Restful',
                blankText: 'É necessário preencher o campo Cidade de Expedição de Título.',
            });
            column1_items.push({
                width: 350,
                xtype: 'rest-autocompletefield',
                fieldLabel: 'Moléstia',
                name: 'molestia',
                displayField: 'unicode',
                allowBlank: true,
                rest: 'rh.parameters.disease.Restful'
            });

            var f = Ext._create('Ext.Panel', {
                layout: 'column',
                items: [{
                    columnWidth: '.5',
                    layout: 'form',
                    items: column1_items,
                },
                {
                    columnWidth: '.5',
                    layout: 'form',
                    items: column2_items,
                },
            ],
        });

        var column = [f];
        return column;
    },

    getCpfField: function (cfg) {
        if (!this._cpfField) {
            cfg = cfg || {};
            Ext.applyIf(cfg, {
                width: '90%',
                name: 'cpf',
                fieldLabel: 'CPF',
                xtype: 'cpffield',
                allowBlank: false,
                validateOnBlur: true,
                scope: this,
                callBackReadNaturalPerson: function (value) {
                    value = value || '';
                    value = value.replace('.', '');
                    value = value.replace('.', '');
                    value = value.replace('-', '');
                    var managerTab = this.scope.myParams('managerTab');
                    if (!this._preventCallBackReadNaturalPerson && managerTab != undefined && value.length == 11) {
                        managerTab.getEmployeePanel()._readNaturalPersonData(value);
                    }
                },
                blankText: 'É necessário preencher este campo.',
            });
            this._cpfField = Ext._create('core.fields.CpfField', cfg);
        }
        return this._cpfField;
    },

    getFotoField: function (link) {
        if (!this._fotoField) {
            var cfg = {};
            Ext.applyIf(cfg, {
                hideLabel: true,
                name: 'foto',
                hideInputDisplay: true,
                height: 196,
                captureWidth: 895,
                captureHeight: 555,
                cropWidth: 555 * 0.75,
                listeners: {
                    scope: this,
                    afterchange: function (field, instance) {
                        var path = [
                            core.callAction('FileUploadController', 'get_image_file', instance.file_hash),
                            '168.196',
                        ].join('');

                        var style = 'url(' + path + ') no-repeat center center';
                        field.ownerCt.body.dom.style.background = style;
                    },
                },
            });
            this._fotoField = Ext._create('core.fields.ImageFileUploadField', cfg);
        }
        return this._fotoField;
    },

    getCivilStatusField: function (cfg) {
        if (!this._civilStatus) {
            cfg = cfg || {};
            Ext.applyIf(cfg, {
                fieldLabel: 'Estado civil',
                hiddenName: 'estado_civil',
                name: 'estado_civil',
                choiceId: 'rh.MARITAL_STATUS',
                width: '90%',
            });
            this._civilStatus = Ext._create('standard.fields.ChoiceField', cfg);
            var store = this._civilStatus.getStore();
            var filter = Ext.decode(store.baseParams.filter);
            store.baseParams.filter = Ext.encode(filter);
            store.load();
        }
        return this._civilStatus;
    },

    getTypeByPossessionField: function (cfg) {
        if (!this._typeByPossession) {
            cfg = cfg || {};
            Ext.applyIf(cfg, {
                fieldLabel: 'Tipo de Servidor',
                hiddenName: 'type_by_possession',
                name: 'type_by_possession',
                choiceId: 'rh.CLASSIF_EMPLOYEE_BY_POSSESSION',
                width: 620,
                valueField: 'cvalue',
            });
            this._typeByPossession = Ext._create('standard.fields.ChoiceField', cfg);
        }
        return this._typeByPossession;
    },
});
