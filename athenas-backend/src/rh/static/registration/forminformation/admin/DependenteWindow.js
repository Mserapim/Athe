Ext._define('rh.registration.forminformation.admin.DependenteWindow', {
    extend: 'core.RestfulWindow',

    rest: 'rh.registration.forminformation.admin.DependenteRestful',
    height: 600,
    width: 600,
    
    constructor: function(cfg) {
        rh.registration.forminformation.admin.DependenteWindow.superclass.constructor.call(this, cfg);
        this.getFormPanel().getForm().loadRecord(cfg);
        this.getFormPanel(cfg);
        
    },

    trueOrFalse: function (value) {
        if (value == true)
            return false;
        else
            return true;
    },

    __getFieldValue: function (field) {
        var value = this.getFormPanel().getForm().findField(field);
        var value = field.getValue();
        if (field.xtype == 'choicefield')
            value = field.lastSelectionText;
        if (field.xtype == 'datefield')
            value = Ext.util.Format.dateRenderer('d/m/Y')(value);
        return value;
    },

    _messageValidated: function (errPersistence) {
        var message = '';
        var validated = this.getValidated();
        if (validated.length > 0 && !errPersistence) {
            message += '<br><p style="color: #000; font-size: 14px; font-weight: bold;">Campos validados:</p>';
            for (i = 0; i < validated.length; i++) {
                var field = this.getFormPanel().getForm().findField(validated[i]);
                var value = this.__getFieldValue(field);
                if (field.xtype == "cpffield")
                    message += '<p style="color: #000; font-size: 14px;">- ' + field.name.substr(0, 1).toUpperCase() + field.name.substr(1) + ': ' + field._hiddenField.value + '</p>';
                else if (field.fieldLabel == undefined)
                    message += '<p style="color: #000; font-size: 14px;">- ' + field.name.substr(0, 1).toUpperCase() + field.name.substr(1) + ': ' + value + '</p>';
                else
                    message += '<p style="color: #000; font-size: 14px;">- ' + field.fieldLabel + ': ' + value + '</p>';
            }
        }
        return message;
    },

    getNotValids: function () {
        //Verificando campos não aceitos
        var notValids = [];
        var validated = this.getValidated();
        for (d = 0; d < this.getFormPanel().getForm().getValues().length; d++) {
            var is_accepted = false;
            for (v = 0; v < validated.length; v++) {
                if (this.getFormPanel().getForm().getValues()[d] == validated[v]) {
                    is_accepted = true;
                    break;
                }
            }
            if (is_accepted == false)
                notValids.push(this.getFormPanel().getForm().getValues()[d]);
        }
        return notValids;
    },

    perform_validation: function (data_send, text) {
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Carregando dados...' });
        data_send['text'] = text;
        mask.show();
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action('RegistrationDependentFormInformationAdmin', 'perform_validation'),
            params: {
                data: JSON.stringify(data_send)
            },
            scope: this,
            success: function (request) {
                mask.hide();
                Ext.Msg.show({
                    title: 'Informação',
                    icon: Ext.Msg.INFO,
                    buttons: Ext.Msg.OK,
                    msg: Ext.decode(request.responseText).message
                });
                values = this.getFormPanel().getForm().getValues()
                this.getFormPanel().getForm().setValues(values);
                this.destroy()
            },
            failure: function (request) {
                mask.hide();
                Ext.Msg.show({
                    title: 'Informação',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: Ext.decode(request.responseText).message
                });
            }
        });

    },

    getValidated: function () {
        // Buscando apenas campos validados pelo RH
        var valids = [];
        for (v in this.getFormPanel().getForm().getValues()) {
            if ((v.indexOf('_valid_')) !== -1) {
                valids.push(v.replace('_valid_', ''));
            }
        }
        return valids;
    },

    _messageNotValidated: function (errPersistence) {
        var message = '';
        var fieldNotValids = this.getNotValids();

        if (errPersistence) {
            message = '<p style="color: #fd0101; font-size: 14px; font-weight: bold;">Nenhum campo ou anexo foi validado.</p>';
        }

        if (fieldNotValids.length > 0) {
            message += '<p style="color: #fd0101; font-size: 14px; font-weight: bold;">Campos não validados:</p>';
            for (i = 0; i < fieldNotValids.length; i++) {
                var field = this.getFormPanel().getForm().findField(fieldNotValids[i]);
                var value = this.__getFieldValue(field);
                if (field.fieldLabel == undefined)
                    message += '<p style="color: #ff3434; font-size: 14px;">- ' + field.name.substr(0, 1).toUpperCase() + field.name.substr(1) + ': ' + value + '</p>';
                else
                    message += '<p style="color: #ff3434; font-size: 14px;">- ' + field.fieldLabel + ': ' + value + '</p>';
            }
        }
        return message;
    },

    _generateDataSendMessage: function (data_send, errPersistence) {
        errPersistence = errPersistence != undefined ? errPersistence : false;
        var message = this._messageNotValidated(errPersistence);
        message += this._messageValidated(errPersistence);
        data_send['text'] = message;
        return data_send;
    },

    getWindowMessageValidation: function (cfg, data_send, type_send) {
        this._windowMessageValidation = Ext._create('rh.registration.forminformation.admin.WindowMessageValidation', {
            father: this,
            data_send: data_send,
            type_send: type_send
        });
        return this._windowMessageValidation;
    },

    _callWindowMessageValidation: function (data_send, type_send) {
        var windowMessageValidation = this.getWindowMessageValidation({}, data_send, type_send);
            windowMessageValidation.show();
    },

    _try_perform_validation: function (cfg) {

        var data_send = {};

        var valids = this.getValidated();
        var valid_fields = []
        for (v = 0; v < valids.length; v++) {
            valid_fields.push(valids[v]);
        }
        data_send['valid_fields'] = valid_fields;
        data_send = this._generateDataSendMessage(data_send, false);
        data_send['dependent_form'] = cfg.values.id

        this.perform_validation(data_send, 'text')

    },

    save: function () {
        this.callback = {};

        rh.registration.forminformation.admin.DependenteWindow.superclass.save.call(this);
    },

    getButtons: function (cfg) {
        if (!this._buttons) {
            this._buttons = [
                {
                    text: 'Validar',
                    handler: function () {
                        this._try_perform_validation(cfg);
                    },
                    scope: this
                },
                // {
                //     text: 'Salvar',
                //     scope: this,
                //     handler: function () {
                //         this.save(true);
                //     }
                // },
                
                {
                    'text': 'Fechar',
                    'scope': this,
                    'handler': this.destroy
                }
            ];
        }

        return this._buttons;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                height: 600,
                width: 600,
                items: [
                    {
                        layout: 'hbox',
                        border: false,
                        items: [
                            {
                                layout: 'form',
                                region: 'center',
                                border: false,
                                style: 'margin-left: 5px',
                                items:
                                    [
                                        {
                                            xtype: 'textfield',
                                            width: 260,
                                            readOnly: true,
                                            enableKeyEvents: true,
                                            disabled: this.trueOrFalse(cfg.values.nome_dependent_can_edit),
                                            name: 'nome_dependent',
                                            fieldLabel: 'Nome do dependente',
                                        },
                                    ]
                            },
                            {
                                layout: 'form',
                                region: 'center',
                                border: false,
                                style: 'margin-left: 10px',
                                items:
                                    [
                                        {
                                            fieldLabel: 'Validar',
                                            xtype: 'checkbox',
                                            name: 'nome_dependent_valid_',
                                            width: 15,
                                            style: 'margin-left: -45px',
                                            checked: this.trueOrFalse(cfg.values.nome_dependent_can_edit),
                                            disabled: this.trueOrFalse(cfg.values.nome_dependent_can_edit),
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
                                style: 'margin-left: 5px',
                                items:
                                    [
                                        {
                                            fieldLabel: 'Sexo do dependente',
                                            xtype: 'combo',
                                            hiddenName: 'sexo_dependent',
                                            name: 'sexo_dependent',
                                            enableKeyEvents: true,
                                            allowBlank: true,
                                            lazyRender: true,
                                            readOnly: true,
                                            disabled: true,
                                            mode: 'local',
                                            triggerAction: 'all',
                                            store: [
                                                ['F', 'FEMININO'],
                                                ['M', 'MASCULINO']
                                            ],
                                            width: 260,
                                        },
                                    ]
                            },
                           
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
                                style: 'margin-left: 5px',
                                items:
                                    [
                                        {
                                            xtype: 'cpffield',
                                            enableKeyEvents: true,
                                            name: 'cpf_dependent',
                                            fieldLabel: 'CPF',
                                            readOnly: true,
                                            width: 260,
                                            disabled: this.trueOrFalse(cfg.values.cpf_dependent_can_edit)
                                        },
                                    ]
                            },
                            {
                                layout: 'form',
                                region: 'center',
                                border: false,
                                style: 'margin-left: 10px',
                                items:
                                    [
                                        {
                                            fieldLabel: 'Validar',
                                            xtype: 'checkbox',
                                            name: 'cpf_dependent_valid_',
                                            width: 15,
                                            style: 'margin-left: -45px',
                                            checked: this.trueOrFalse(cfg.values.cpf_dependent_can_edit),
                                            disabled: this.trueOrFalse(cfg.values.cpf_dependent_can_edit)
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
                                style: 'margin-left: 5px',
                                items:
                                    [
                                        {
                                            name: "data_nascimento_dependent",
                                            fieldLabel: "Data de Nascimento",
                                            xtype: "datefield",
                                            readOnly: true,
                                            allowBlank: true,
                                            width: 260,
                                            disabled: true
                                        },
                                    ]
                            },
                            
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
                                style: 'margin-left: 5px',
                                items:
                                    [
                                        {
                                            xtype: 'choicefield',
                                            fieldLabel: "Tipo de Parentesco *",
                                            hiddenName: 'grau_parentesco',
                                            choiceId: 'rh.GRAU_PARENTESCO_CHOICES',
                                            readOnly: true,
                                            width: 260,
                                            disabled: true
                                        },
                                    ]
                            },
                            
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
                                style: 'margin-left: 5px',
                                items:
                                    [
                                        {
                                            xtype: 'choicefield',
                                            fieldLabel: 'Tipo *',
                                            hiddenName: 'tipo',
                                            choiceId: 'rh.DEPENDENT_TYPE',
                                            readOnly: true,
                                            width: 260,
                                            disabled: this.trueOrFalse(cfg.values.tipo_can_edit)
                                        },
                                    ]
                            },
                            {
                                layout: 'form',
                                region: 'center',
                                border: false,
                                style: 'margin-left: 10px',
                                items:
                                    [
                                        {
                                            fieldLabel: 'Validar',
                                            xtype: 'checkbox',
                                            name: 'tipo_valid_',
                                            width: 15,
                                            style: 'margin-left: -45px',
                                            checked: this.trueOrFalse(cfg.values.tipo_can_edit),
                                            disabled: this.trueOrFalse(cfg.values.tipo_can_edit)
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
                                style: 'margin-left: 5px',
                                items:
                                    [
                                        {
                                            xtype:'radiogroup',
                                            fieldLabel: 'Incapacidade',
                                            columns: 1,
                                            style: 'margin-left: 5px',
                                            disabled: true,
                                            readOnly: true,
                                            items: [
                                                {
                                                    xtype:'radio',
                                                    inputValue:'true',
                                                    boxLabel: 'Sim',
                                                    checked: cfg.values.incapacity ==true,
                                                    name: 'incapacity'
                                                },
                                                {
                                                    xtype:'radio',
                                                    inputValue:'false',
                                                    boxLabel: 'Não',
                                                    checked: cfg.values.incapacity ==false,
                                                    name: 'incapacity'
                                                },
                                            ]
                                        }
                                    ]
                            },

                        ]
                    },
                ]
            });
            
        return this._formPanel;
    },

});

