Ext.ns('rh.registration');
Ext._define('rh.registration.forminformation.admin.Window', {
    extend: 'core.RestfulWindow',
    rest: 'rh.registration.forminformation.admin.Restful',
    width: 1000,
    height: 600,
    autoScroll: true,

    constructor: function (cfg) {
        cfg = (cfg ? cfg : {});
        diffs_ = [];
        this.values = cfg.values;
        rh.registration.forminformation.admin.Window.superclass.constructor.call(this, cfg);
        this.getFormGed().setForm(cfg.oId === undefined ? null : cfg.oId);
    },

    perform_validation: function (data_send, text) {
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Carregando dados...' });
        data_send['text'] = text;
        mask.show();
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action('RegistrationFormInformationAdmin', 'perform_validation'),
            params: {
                data: JSON.stringify(data_send)
            },
            scope: this,
            success: function (request) {
                mask.hide();
                var rst = Ext.decode(request.responseText);
                var callConfirmValidationWindow = false;
                if (rst.errors) {
                    var message = '';
                    for (i = 0; i < rst.errors.length; i++) {
                        if (rst.errors[i].field == 'err_finish_validation') {
                            callConfirmValidationWindow = true;
                            break;
                        }
                        if (rst.errors[i].field == 'err_finish_persistence') {
                            callConfirmValidationWindow = true;
                            break;
                        }
                    }
                }
                if (rst.success) {
                    this.parentGrid.getStore().reload();
                    this.parentGrid.ownerCt.getValidation().getStore().reload();
                    this.destroy();
                }
                else if (callConfirmValidationWindow) {
                    this._callConfirmValidationWindow(data_send, rst.errors);
                }
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

    getOnlyDiffTrue: function () {
        // Buscando campos que foram alterados pelo Servidor
        if (this._onlyDiffTrue == undefined) {
            this._onlyDiffTrue = [];
            for (v in this.selecteDataGridFormInformation) {
                if ((v.indexOf('_diff')) !== -1) {
                    if (this.selecteDataGridFormInformation[v] == true) {
                        this._onlyDiffTrue.push(v.replace('_diff', ''));
                    }
                }
            }
        }
        return this._onlyDiffTrue;
    },

    getAccepted: function () {
        //Verificando apenas campos aceitos pelo RH
        var accepteds = [];
        var validated = this.getValidated();
        for (d = 0; d < this.getOnlyDiffTrue().length; d++) {
            var is_accepted = false;
            for (v = 0; v < validated.length; v++) {
                if (this.getOnlyDiffTrue()[d] == validated[v]) {
                    is_accepted = true;
                    accepteds.push(validated[v])
                    break;
                }
            }
        }
        return accepteds;
    },

    getNotValids: function () {
        //Verificando campos não aceitos
        var notValids = [];
        var validated = this.getValidated();
        for (d = 0; d < this.getOnlyDiffTrue().length; d++) {
            var is_accepted = false;
            for (v = 0; v < validated.length; v++) {
                if (this.getOnlyDiffTrue()[d] == validated[v]) {
                    is_accepted = true;
                    break;
                }
            }
            if (is_accepted == false)
                notValids.push(this.getOnlyDiffTrue()[d]);
        }
        return notValids;
    },

    getAttachments: function () {
        return this.getFormGed().getStore().data.items;
    },

    getAttachmentValid: function () {
        return this.getFormGed().getSelectionModel().getSelections();
    },

    getAttachmentNotValid: function () {
        var valids = [];
        var notValids = [];

        for (i = 0; i < this.getAttachmentValid().length; i++)
            valids.push(this.getAttachmentValid()[i].data.pk);

        for (i = 0; i < this.getAttachments().length; i++)
            if (valids.indexOf(this.getAttachments()[i].data.pk) == -1)
                notValids.push(this.getAttachments()[i]);

        return notValids;
    },

    _messageNotValidated: function (errPersistence) {
        var message = '';
        var message_err = '';
        var fieldNotValids = this.getNotValids();
        var digitalDocumentsNotValids = this.getAttachmentNotValid();

        if (errPersistence) {
            message = '<p style="color: #fd0101; font-size: 14px; font-weight: bold;">Nenhum campo ou anexo foi validado.</p>';
            fieldNotValids = this.getOnlyDiffTrue();
            digitalDocumentsNotValids = [];
            for (i = 0; i < this.getAttachments().length; i++)
                digitalDocumentsNotValids.push(this.getAttachments()[i]);
        }

        if (fieldNotValids.length > 0) {
            message += '<p style="color: #fd0101; font-size: 14px; font-weight: bold;">Campos não validados:</p>';
            for (i = 0; i < fieldNotValids.length; i++) {
                var field = this.getFormPanel().getForm().findField(fieldNotValids[i]);
                var value = this.__getFieldValue(field);
                if (field.name == 'foto') {
                    value = '';
                }
                if (field.name == 'doador' || field.name == 'uniao_estavel' || field.name == 'address_outsider' || field.name == 'phone_outsider' || field.name == 'address_new') {
                    value = this._translateBooleanField(value);
                }
                if (field.fieldLabel == undefined)
                    message += '<p style="color: #ff3434; font-size: 14px;">- ' + field.name.substr(0, 1).toUpperCase() + field.name.substr(1) + ': ' + value + '</p>';
                else
                    message += '<p style="color: #ff3434; font-size: 14px;">- ' + field.fieldLabel + ': ' + value + '</p>';
            }
        }

        if (digitalDocumentsNotValids.length > 0) {
            message += '<p style="color: #fd0101; font-size: 14px; font-weight: bold;">Documentos não validados:</p>';
            for (i = 0; i < digitalDocumentsNotValids.length; i++)
                message += '<p style="color: #ff3434; font-size: 14px;">- ' + digitalDocumentsNotValids[i].data.document_type_display + '</p>';
        }

        return message;
    },

    _translateBooleanField: function (value) {
        if (value) {
            return 'Sim';
        } else {
            return 'Não'
        }
    },

    _messageValidated: function (errPersistence) {
        var message = '';
        var validated = this.getValidated();
        if (validated.length > 0 && !errPersistence) {
            message += '<br><p style="color: #000; font-size: 14px; font-weight: bold;">Campos validados:</p>';
            for (i = 0; i < validated.length; i++) {
                var field = this.getFormPanel().getForm().findField(validated[i]);
                var value = this.__getFieldValue(field);
                if (field.name == 'foto') {
                    value = '';
                }
                if (field.name == 'doador' || field.name == 'uniao_estavel' || field.name == 'address_outsider' || field.name == 'phone_outsider' || field.name == 'address_new') {
                    value = this._translateBooleanField(value);
                }
                if (field.fieldLabel == undefined)
                    message += '<p style="color: #000; font-size: 14px;">- ' + field.name.substr(0, 1).toUpperCase() + field.name.substr(1) + ': ' + value + '</p>';
                else
                    message += '<p style="color: #000; font-size: 14px;">- ' + field.fieldLabel + ': ' + value + '</p>';
            }
        }
        var selected_documents = this.getAttachmentValid();
        if (selected_documents.length > 0 && !errPersistence) {
            message += '<p style="color: #000; font-size: 14px; font-weight: bold;">Documentos validados:</p>';
            for (i = 0; i < selected_documents.length; i++)
                message += '<p style="color: #000; font-size: 14px;">- ' + selected_documents[i].data.document_type_display + '<p/>';
        }
        return message;
    },

    __getFieldValue: function (field) {
        var value = this.selecteDataGridFormInformation[field.name];
        var value = field.getValue();
        if (field.xtype == 'rest-autocompletefield')
            value = this.selecteDataGridFormInformation[field.name + '_unicode'];
        if (field.xtype == 'combo')
            value = this.selecteDataGridFormInformation[field.name];
        if (field.xtype == 'choicefield')
            value = this.selecteDataGridFormInformation[field.name + '_display'];
        if (field.xtype == 'checkbox')
            value = value;
        if (field.xtype == 'datefield')
            value = Ext.util.Format.dateRenderer('d/m/Y')(value);
        if (field.xtype == 'ged-fileuploadfield')
            value = value;
        return value;
    },

    _try_perform_validation: function (cfg) {
        var fields = this.selecteDataGridFormInformation;

        var data_send = {};
        data_send['form'] = fields.pk;

        var valids = this.getValidated();
        var valid_fields = []
        for (v = 0; v < valids.length; v++) {
            valid_fields.push(valids[v]);
        }
        data_send['valid_fields'] = valid_fields;

        var digital_documents = []
        var selected_documents = this.getAttachmentValid();
        for (i = 0; i < selected_documents.length; i++) {
            digital_documents.push(selected_documents[i].data.pk)
        }

        data_send['digital_documents'] = digital_documents;
        data_send = this._generateDataSendMessage(data_send, false);

        this._callWindowMessageValidation(data_send, 'VALIDATION');
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
        setTimeout( () =>{
            if (this.getFormGed().getStore().getTotalCount() > 0 && data_send['digital_documents'].length == 0 && type_send != 'CONFIRMATION')
                Ext.Msg.show({
                    wait: true,
                    scope: this,
                    title: 'PERGUNTA',
                    icon: Ext.Msg.QUESTION,
                    buttons: Ext.Msg.OKCANCEL,
                    style: 'background-color: yellow',
                    msg: 'Deseja validar sem marcar nenhum Anexo como aceito?',
                    fn: function (button) {
                        if (button == 'ok')
                            windowMessageValidation.show();
                    },
                });
                
            else {
                windowMessageValidation.show();
            }
        }, 1000);
    },

    _callConfirmValidationWindow: function (data_send, errors) {
        var message = '';
        var message_err_finish_validation = '';
        var message_err_finish_persistence = '';
        data_send['message_err'] = '';
        if (errors) {
            var buff = '';
            for (i = 0; i < errors.length; i++) {
                for (x = 0; x < errors[i].values.length; x++) {
                    if (errors[i].field == 'err_finish_validation') {
                        message_err_finish_validation = '<br><b>' + errors[i].values[x] + '</b>';
                    }
                    else if (errors[i].field == 'err_finish_persistence') {
                        message_err_finish_persistence = '<br><b>' + errors[i].values[x] + '</b>';
                    }
                    else {
                        buff += '<br>' + errors[i].values[x];
                    }
                }
            }
            if (message_err_finish_persistence != '')
                data_send['message_err'] += message_err_finish_persistence;
            data_send['message_err'] += buff;
            if (message_err_finish_validation != '')
                data_send['message_err'] += message_err_finish_validation;
            data_send['message_err'] += buff;
            message += '<br>' + buff;
        }
        data_send = this._generateDataSendMessage(data_send, message_err_finish_persistence != '' ? true : false);
        if (message != '') {
            if (message_err_finish_validation == '')
                data_send['text'] += message;
        }
        this._callWindowMessageValidation(data_send, 'CONFIRMATION');
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
                {
                    'text': 'Fechar',
                    'scope': this,
                    'handler': this.destroy
                }
            ];
        }

        return this._buttons;
    },

    trueOrFalse: function (value) {
        if (value == true)
            return false;
        else
            return true;
    },

    selectAll: function (cfg) {
        var values = cfg.scope.selecteDataGridFormInformation;
        for (v in values) {
            if ((v.indexOf('_diff')) !== -1) {
                if (values[v] == true) {
                    try {
                        var field = this.getFormPanel().getForm().findField(v.replace('_diff', '') + '_valid_');
                        if (field != undefined)
                            field.setValue(true);
                        else
                            console.info('Campo ' + v + ' não encontrado!')
                    } catch (err) {
                        console.exception(err);
                    }
                }
            }
        }
    },

    deSelectAll: function (cfg) {
        var values = cfg.scope.selecteDataGridFormInformation;
        for (v in values) {
            if ((v.indexOf('_diff')) !== -1) {
                if (values[v] == true) {
                    this.getFormPanel().getForm().findField(v.replace('_diff', '') + '_valid_').setValue(false)
                }
            }
        }
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

    getFormGed: function () {
        if (!this._gedGrid)
            this._gedGrid = new rh.registration.forminformation.ged.Admin({
                title: 'Anexo(s)',
                layout: 'form',
                height: 230,
                anchor: '100% 100%',
                border: false,
            });

        return this._gedGrid;
    },

    getFotoField: function (cfg) {
        if (!this._fotoField) {
            this._fotoField = new toolkit.plugins.FileUpload({
                fieldLabel: 'Foto',
                name: 'foto',
                xtype: 'ged-fileuploadfield',
                allowBlank: true,
                types: ['image/jpeg', 'image/png'],
                width: 175,
                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.foto_diff : false)
            });
        }

        return this._fotoField;
    },

    tabDependent: function (cfg) {
        if (!this._tabDependent) {
            this._tabDependent = Ext._create('Ext.Panel', {


                xtype: 'fieldset',
                title: 'Dependentes de IR',
                name: 'fieldServidor',
                items: [
                    this.getDependentGrid(cfg)
                ]
            });
        }
        return this._tabDependent;
    },

    getDependentGrid: function(cfg) {
        if(!this._dependentGrid) {
            this._dependentGrid = Ext._create('rh.registration.forminformation.admin.DependenteGrid',{
                height: 450,
                width: 450,
            });           
        }
        if (cfg.selecteDataGridFormInformation){
            this._dependentGrid.setFilterProperty('employee', cfg.selecteDataGridFormInformation.employee, 100)
        }
        return this._dependentGrid;
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [{
                    layout: 'border',
                    border: false,
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
                                    title: 'Opções',
                                    name: 'fieldMarcarDesmarcar',
                                    buttons:
                                        [
                                            {
                                                'text': 'Marcar todos',
                                                'scope': this,
                                                'handler': this.selectAll
                                            },
                                            {
                                                'text': 'Desmarcar todos',
                                                'scope': this,
                                                'handler': this.deSelectAll
                                            }
                                        ],
                                },
                                {
                                    xtype: 'fieldset',
                                    title: 'Dados pessoais',
                                    name: 'fieldServidor',
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
                                                                name: 'nome',
                                                                fieldLabel: 'Nome',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.nome_diff : false)
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
                                                                name: 'nome_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.nome_diff : false)
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
                                                                xtype: 'textfield',
                                                                width: 260,
                                                                readOnly: true,
                                                                enableKeyEvents: true,
                                                                name: 'social_name',
                                                                fieldLabel: 'Nome Social',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.social_name_diff : false)
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
                                                                name: 'social_name_valid_',
                                                                style: 'margin-left: -45px',
                                                                width: 15,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.social_name_diff : false)
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
                                                                xtype: 'textfield',
                                                                width: 260,
                                                                readOnly: true,
                                                                enableKeyEvents: true,
                                                                name: 'genero',
                                                                fieldLabel: 'Identidade de Gênero',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.genero_diff : false)
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
                                                                name: 'genero_valid_',
                                                                style: 'margin-left: -45px',
                                                                width: 15,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.genero_diff : false)
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
                                                                xtype: 'textfield',
                                                                width: 260,
                                                                readOnly: true,
                                                                enableKeyEvents: true,
                                                                name: 'nome_conjuge',
                                                                fieldLabel: 'Nome Cônjuge/Companheiro',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.nome_conjuge_diff : false)
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
                                                                name: 'nome_conjuge_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.nome_conjuge_diff : false)
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
                                                                xtype: 'textfield',
                                                                width: 260,
                                                                readOnly: true,
                                                                enableKeyEvents: true,
                                                                name: 'nome_mae',
                                                                fieldLabel: 'Nome da Mãe',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.nome_mae_diff : false)
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
                                                                name: 'nome_mae_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.nome_mae_diff : false)
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
                                                                xtype: 'textfield',
                                                                width: 260,
                                                                readOnly: true,
                                                                enableKeyEvents: true,
                                                                name: 'nome_pai',
                                                                fieldLabel: 'Nome do Pai',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.nome_pai_diff : false)
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
                                                                name: 'nome_pai_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.nome_pai_diff : false)
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
                                                                xtype: 'combo',
                                                                fieldLabel: 'Sexo',
                                                                allowBlank: true,
                                                                lazyRender: true,
                                                                mode: 'local',
                                                                triggerAction: 'all',
                                                                store: [
                                                                    ['F', 'FEMININO'],
                                                                    ['M', 'MASCULINO']
                                                                ],
                                                                name: 'sexo',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.sexo_diff : false)
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
                                                                name: 'sexo_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.sexo_diff : false)
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
                                                                fieldLabel: 'Orientação Sexual',
                                                                xtype: 'choicefield',
                                                                choiceId: 'rh.SEXUAL_ORIENTATION',
                                                                name: 'sexual_orientation',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.sexual_orientation_diff : false)

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
                                                                name: 'sexual_orientation_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.sexual_orientation_diff : false)
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
                                                                fieldLabel: 'Raça/Cor',
                                                                xtype: 'choicefield',
                                                                name: 'raca_cor',
                                                                choiceId: 'rh.TYPE_RACE',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.raca_cor_diff : false)
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
                                                                name: 'raca_cor_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.raca_cor_diff : false)
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
                                                                fieldLabel: 'Estado civil',
                                                                xtype: 'choicefield',
                                                                name: 'estado_civil',
                                                                width: 260,
                                                                readOnly: true,
                                                                choiceId: 'rh.MARITAL_STATUS',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.estado_civil_diff : false)
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
                                                                name: 'estado_civil_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.estado_civil_diff : false)
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
                                                                fieldLabel: 'Sangue',
                                                                xtype: 'choicefield',
                                                                name: 'sangue',
                                                                width: 260,
                                                                readOnly: true,
                                                                choiceId: 'rh.BLOOD',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.sangue_diff : false)
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
                                                                name: 'sangue_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.sangue_diff : false)
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
                                                                xtype: 'choicefield',
                                                                fieldLabel: 'Fator RH',
                                                                choiceId: 'rh.FACTOR_RH',
                                                                name: 'fator_rh',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.fator_rh_diff : false)
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
                                                                name: 'fator_rh_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.fator_rh_diff : false)
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
                                                                fieldLabel: 'Doador',
                                                                xtype: 'checkbox',
                                                                name: 'doador',
                                                                width: 260,
                                                                disabled: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.doador_diff : false)
                                                            },
                                                        ]
                                                },
                                                {
                                                    layout: 'form',
                                                    region: 'center',
                                                    border: false,
                                                    style: 'margin-left: 12px',
                                                    items:
                                                        [
                                                            {
                                                                fieldLabel: 'Validar',
                                                                xtype: 'checkbox',
                                                                name: 'doador_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.doador_diff : false)
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
                                                                fieldLabel: 'União Estável',
                                                                xtype: 'checkbox',
                                                                name: 'uniao_estavel',
                                                                width: 260,
                                                                disabled: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.uniao_estavel_diff : false)
                                                            },
                                                        ]
                                                },
                                                {
                                                    layout: 'form',
                                                    region: 'center',
                                                    border: false,
                                                    style: 'margin-left: 12px',
                                                    items:
                                                        [
                                                            {
                                                                fieldLabel: 'Validar',
                                                                xtype: 'checkbox',
                                                                name: 'uniao_estavel_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.uniao_estavel_diff : false)
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
                                                                xtype: 'rest-autocompletefield',
                                                                fieldLabel: 'Naturalidade',
                                                                name: 'municipio_naturalidade',
                                                                displayField: 'unicode',
                                                                allowBlank: true,
                                                                rest: 'rh.localidade.Restful',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.municipio_naturalidade_diff : false)
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
                                                                name: 'municipio_naturalidade_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.municipio_naturalidade_diff : false)
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
                                                                xtype: 'rest-autocompletefield',
                                                                fieldLabel: 'Nacionalidade',
                                                                name: 'nationality',
                                                                displayField: 'unicode',
                                                                allowBlank: true,
                                                                rest: 'rh.country.Restful',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.nationality_diff : false)
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
                                                                name: 'nationality_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.nationality_diff : false)
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
                                                                xtype: 'rest-autocompletefield',
                                                                fieldLabel: 'País de nascimento',
                                                                name: 'nationality_birth',
                                                                displayField: 'unicode',
                                                                allowBlank: true,
                                                                rest: 'rh.country.Restful',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.nationality_birth_diff : false)
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
                                                                name: 'nationality_birth_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.nationality_birth_diff : false)
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
                                                                xtype: 'textfield',
                                                                width: 260,
                                                                readOnly: true,
                                                                enableKeyEvents: true,
                                                                name: 'email_institucional',
                                                                fieldLabel: 'E-mail Institucional',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.email_institucional_diff : false)
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
                                                                name: 'email_institucional_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.email_institucional_diff : false)
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
                                                                name: 'data_nascimento',
                                                                fieldLabel: 'Data nascimento',
                                                                xtype: 'datefield',
                                                                allowBlank: true,
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.data_nascimento_diff : false)
                                                            }
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
                                                                name: 'data_nascimento_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.data_nascimento_diff : false)
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
                                                                fieldLabel: 'Grau de Instrução',
                                                                xtype: 'choicefield',
                                                                choiceId: 'rh.DEGREE_EDUCATION',
                                                                hiddenName: 'grau_instrucao',
                                                                name: 'grau_instrucao',
                                                                width: 260,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.grau_instrucao_diff : false)
                                                            }
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
                                                                name: 'grau_instrucao_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.grau_instrucao_diff : false)
                                                            }
                                                        ]
                                                }
                                            ]
                                        },
                                    ]
                                },
                                {
                                    xtype: 'fieldset',
                                    title: 'Endereço',
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
                                                                fieldLabel: 'Endereço no exterior',
                                                                xtype: 'checkbox',
                                                                name: 'address_outsider',
                                                                width: 260,
                                                                disabled: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.address_outsider_diff : false)
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
                                                                name: 'address_outsider_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.address_outsider_diff : false)
                                                            }
                                                        ]
                                                }
                                            ],
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
                                                                xtype: 'rest-autocompletefield',
                                                                fieldLabel: 'Cidade',
                                                                name: 'address_city',
                                                                displayField: 'unicode',
                                                                allowBlank: true,
                                                                rest: 'rh.localidade.Restful',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.address_city_diff : false)
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
                                                                name: 'address_city_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.address_city_diff : false)
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
                                                                xtype: 'textfield',
                                                                fieldLabel: 'Cidade no Exterior',
                                                                name: 'address_outsider_citty',
                                                                allowBlank: true,
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.address_outsider_citty_diff : false)
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
                                                                name: 'address_outsider_citty_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.address_outsider_citty_diff : false)
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
                                                                fieldLabel: 'Endereço Novo',
                                                                xtype: 'checkbox',
                                                                name: 'address_new',
                                                                width: 260,
                                                                disabled: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.address_new_diff : false)
                                                            }
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
                                                                name: 'address_new_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.address_new_diff : false)
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
                                                                fieldLabel: 'Tipo Endereço',
                                                                xtype: 'choicefield',
                                                                choiceId: 'rh.TYPE_ADDRESS',
                                                                name: 'address_type_address',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.address_type_address_diff : false)

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
                                                                name: 'address_type_address_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.address_type_address_diff : false)
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
                                                                fieldLabel: 'Tipo Logradouro',
                                                                xtype: 'choicefield',
                                                                choiceId: 'rh.TYPE_STREET',
                                                                name: 'address_type_street',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.address_type_street_diff : false)

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
                                                                name: 'address_type_street_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.address_type_street_diff : false)
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
                                                                fieldLabel: 'Logradouro',
                                                                xtype: 'textfield',
                                                                name: 'address_public_place',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.address_public_place_diff : false)

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
                                                                name: 'address_public_place_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.address_public_place_diff : false)
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
                                                                fieldLabel: 'Número',
                                                                xtype: 'textfield',
                                                                name: 'address_number',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.address_number_diff : false)

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
                                                                name: 'address_number_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.address_number_diff : false)
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
                                                                fieldLabel: 'CEP',
                                                                xtype: 'textfield',
                                                                name: 'address_zip_code',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.address_zip_code_diff : false)

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
                                                                name: 'address_zip_code_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.address_zip_code_diff : false)
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
                                                                fieldLabel: 'Bairro',
                                                                xtype: 'textfield',
                                                                name: 'address_district',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.address_district_diff : false)

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
                                                                name: 'address_district_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.address_district_diff : false)
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
                                                                fieldLabel: 'Complemento',
                                                                xtype: 'textfield',
                                                                name: 'address_complement',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.address_complement_diff : false)

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
                                                                name: 'address_complement_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.address_complement_diff : false)
                                                            }
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
                                                                xtype: 'rest-autocompletefield',
                                                                fieldLabel: 'País(em caso de residência no exterior)',
                                                                name: 'address_country',
                                                                displayField: 'unicode',
                                                                allowBlank: true,
                                                                rest: 'rh.country.Restful',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.address_country_diff : false)
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
                                                                name: 'address_country_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.address_country_diff : false)
                                                            }
                                                        ]
                                                }
                                            ]
                                        },
                                    ]
                                },
                                {
                                    xtype: 'fieldset',
                                    title: 'Telefones',
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
                                                                fieldLabel: 'Nome/Contato Emergência',
                                                                xtype: 'textfield',
                                                                name: 'contact_emergency_name',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.contact_emergency_name_diff : false)

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
                                                                name: 'contact_emergency_name_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.contact_emergency_name_diff : false)
                                                            }
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
                                                style: 'margin-left: 5px',
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
                                                            hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.contact_emergency_phone_kinship_diff : false)
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
                                                                name: 'contact_emergency_phone_kinship_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.contact_emergency_phone_kinship_diff : false)
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
                                                                fieldLabel: 'Telefone/Contato Emergência',
                                                                xtype: 'textfield',
                                                                name: 'contact_emergency_phone',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.contact_emergency_phone_diff : false)

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
                                                                name: 'contact_emergency_phone_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.contact_emergency_phone_diff : false)
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
                                                                fieldLabel: 'Telefone/Principal',
                                                                xtype: 'textfield',
                                                                name: 'phone_main',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.phone_main_diff : false)

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
                                                                name: 'phone_main_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.phone_main_diff : false)
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
                                                                fieldLabel: 'Telefone no exterior',
                                                                xtype: 'checkbox',
                                                                name: 'phone_outsider',
                                                                width: 260,
                                                                disabled: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.phone_outsider_diff : false)
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
                                                                name: 'phone_outsider_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.phone_outsider_diff : false)
                                                            }
                                                        ]
                                                }
                                            ]
                                        },
                                    ]
                                },
                                {
                                    xtype: 'fieldset',
                                    title: 'Documentos',
                                    name: 'fieldServidor',
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
                                                                name: 'cpf',
                                                                fieldLabel: 'CPF',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.cpf_diff : false)
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
                                                                name: 'cpf_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.cpf_diff : false)
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
                                                                xtype: 'textfield',
                                                                width: 260,
                                                                readOnly: true,
                                                                enableKeyEvents: true,
                                                                name: 'rg',
                                                                fieldLabel: 'RG',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.rg_diff : false)
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
                                                                name: 'rg_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.rg_diff : false)
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
                                                                fieldLabel: 'RG Órgão',
                                                                xtype: 'textfield',
                                                                name: 'rg_orgao',
                                                                enableKeyEvents: true,
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.rg_orgao_diff : false)
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
                                                                name: 'rg_orgao_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.rg_orgao_diff : false)
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
                                                                name: 'rg_data_expedicao',
                                                                fieldLabel: 'RG Data de Expedição',
                                                                xtype: 'datefield',
                                                                allowBlank: true,
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.rg_data_expedicao_diff : false)
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
                                                                name: 'rg_data_expedicao_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.rg_data_expedicao_diff : false)
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
                                                                xtype: 'rest-autocompletefield',
                                                                fieldLabel: 'RG UF',
                                                                name: 'rg_uf',
                                                                displayField: 'unicode',
                                                                allowBlank: true,
                                                                rest: 'rh.estado.Restful',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.rg_uf_diff : false)
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
                                                                name: 'rg_uf_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.rg_uf_diff : false)
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
                                                                fieldLabel: 'CNH',
                                                                xtype: 'textfield',
                                                                name: 'cnh',
                                                                enableKeyEvents: true,
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.cnh_diff : false)
                                                            }
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
                                                                name: 'cnh_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.cnh_diff : false)
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
                                                                name: 'cnh_first_date',
                                                                fieldLabel: 'CNH Primeira Data Expedição',
                                                                xtype: 'datefield',
                                                                allowBlank: true,
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.cnh_first_date_diff : false)
                                                            }
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
                                                                name: 'cnh_first_date_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.cnh_first_date_diff : false)
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
                                                                fieldLabel: 'CNH Categoria',
                                                                xtype: 'textfield',
                                                                name: 'cnh_categoria',
                                                                enableKeyEvents: true,
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.cnh_categoria_diff : false)
                                                            }
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
                                                                name: 'cnh_categoria_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.cnh_categoria_diff : false)
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
                                                                name: 'cnh_expedition_date',
                                                                fieldLabel: 'CNH Data Expedição',
                                                                xtype: 'datefield',
                                                                allowBlank: true,
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.cnh_expedition_date_diff : false)
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
                                                                name: 'cnh_expedition_date_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.cnh_expedition_date_diff : false)
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
                                                                name: 'cnh_validity_date',
                                                                fieldLabel: 'CNH Data Validade',
                                                                xtype: 'datefield',
                                                                allowBlank: true,
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.cnh_validity_date_diff : false)
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
                                                                name: 'cnh_validity_date_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.cnh_validity_date_diff : false)
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
                                                                xtype: 'rest-autocompletefield',
                                                                fieldLabel: 'CNH UF',
                                                                name: 'cnh_state',
                                                                displayField: 'unicode',
                                                                allowBlank: true,
                                                                rest: 'rh.estado.Restful',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.cnh_state_diff : false)
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
                                                                name: 'cnh_state_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.cnh_state_diff : false)
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
                                                                fieldLabel: 'CTPS',
                                                                xtype: 'textfield',
                                                                name: 'ctps',
                                                                enableKeyEvents: true,
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.ctps_diff : false)
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
                                                                name: 'ctps_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.ctps_diff : false)
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
                                                                fieldLabel: 'Série de CTPS',
                                                                xtype: 'textfield',
                                                                name: 'serie_ctps',
                                                                enableKeyEvents: true,
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.serie_ctps_diff : false)
                                                            }
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
                                                                name: 'serie_ctps_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.serie_ctps_diff : false)
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
                                                                xtype: 'rest-autocompletefield',
                                                                fieldLabel: 'CTPS UF',
                                                                name: 'ctps_state',
                                                                displayField: 'unicode',
                                                                allowBlank: true,
                                                                rest: 'rh.estado.Restful',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.ctps_state_diff : false)
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
                                                                name: 'ctps_state_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.ctps_state_diff : false)
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
                                                                xtype: 'textfield',
                                                                width: 260,
                                                                readOnly: true,
                                                                enableKeyEvents: true,
                                                                name: 'pis_pasep',
                                                                fieldLabel: 'PIS/PASEP',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.pis_pasep_diff : false)
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
                                                                name: 'pis_pasep_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.pis_pasep_diff : false)
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
                                                                fieldLabel: 'Reservista',
                                                                xtype: 'textfield',
                                                                name: 'reservista',
                                                                enableKeyEvents: true,
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.reservista_diff : false)
                                                            }
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
                                                                name: 'reservista_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.reservista_diff : false)
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
                                                                fieldLabel: 'Classe de Reservista',
                                                                xtype: 'textfield',
                                                                name: 'classe_reservista',
                                                                enableKeyEvents: true,
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.classe_reservista_diff : false)
                                                            }
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
                                                                name: 'classe_reservista_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.classe_reservista_diff : false)
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
                                                                fieldLabel: 'Conselho Profissional - Número',
                                                                xtype: 'textfield',
                                                                name: 'professional_council',
                                                                enableKeyEvents: true,
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.professional_council_diff : false)
                                                            }
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
                                                                name: 'professional_council_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.professional_council_diff : false)
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
                                                                xtype: 'rest-autocompletefield',
                                                                fieldLabel: 'Conselho Profissional - UF',
                                                                name: 'professional_council_state',
                                                                displayField: 'unicode',
                                                                allowBlank: true,
                                                                rest: 'rh.estado.Restful',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.professional_council_state_diff : false)
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
                                                                name: 'professional_council_state_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.professional_council_state_diff : false)
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
                                                                name: 'professional_council_expedition_date',
                                                                fieldLabel: 'Conselho Profissional - Data de Expedição',
                                                                xtype: 'datefield',
                                                                allowBlank: true,
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.professional_council_expedition_date_diff : false)
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
                                                                name: 'professional_council_expedition_date_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.professional_council_expedition_date_diff : false)
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
                                                                name: 'professional_council_validity_date',
                                                                fieldLabel: 'Conselho Profissional - Data de Validate',
                                                                xtype: 'datefield',
                                                                allowBlank: true,
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.professional_council_validity_date_diff : false)
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
                                                                name: 'professional_council_validity_date_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.professional_council_validity_date_diff : false)
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
                                                                xtype: 'textfield',
                                                                width: 260,
                                                                readOnly: true,
                                                                enableKeyEvents: true,
                                                                name: 'professional_council_issuer',
                                                                fieldLabel: 'Conselho Profissional - Órgão Emissor',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.professional_council_issuer_diff : false)
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
                                                                name: 'professional_council_issuer_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.professional_council_issuer_diff : false)
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
                                                                xtype: 'textfield',
                                                                width: 260,
                                                                readOnly: true,
                                                                enableKeyEvents: true,
                                                                name: 'titulo_eleitor',
                                                                fieldLabel: 'Título de Eleitor',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.titulo_eleitor_diff : false)
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
                                                                name: 'titulo_eleitor_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.titulo_eleitor_diff : false)
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
                                                                fieldLabel: 'Zona de Título',
                                                                xtype: 'textfield',
                                                                name: 'zona_titulo',
                                                                enableKeyEvents: true,
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.zona_titulo_diff : false)
                                                            }
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
                                                                name: 'zona_titulo_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.zona_titulo_diff : false)
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
                                                                fieldLabel: 'Seção de Título',
                                                                xtype: 'textfield',
                                                                name: 'secao_titulo',
                                                                enableKeyEvents: true,
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.secao_titulo_diff : false)
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
                                                                name: 'secao_titulo_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.secao_titulo_diff : false)
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
                                                                xtype: 'rest-autocompletefield',
                                                                fieldLabel: 'Cidade de Expedição de Título',
                                                                name: 'municipio_titulo',
                                                                displayField: 'unicode',
                                                                allowBlank: true,
                                                                rest: 'rh.localidade.Restful',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.municipio_titulo_diff : false)
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
                                                                name: 'municipio_titulo_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.municipio_titulo_diff : false)
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
                                                                fieldLabel: 'Tempo de permanência',
                                                                xtype: 'choicefield',
                                                                choiceId: 'rh.IMMIGRANTE_RESIDENCE_TIME',
                                                                name: 'immigrant_residence_time',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.immigrant_residence_time_diff : false)
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
                                                                name: 'immigrant_residence_time_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.immigrant_residence_time_diff : false)
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
                                                                fieldLabel: 'Condição de ingresso',
                                                                xtype: 'choicefield',
                                                                choiceId: 'rh.IMMIGRANTE_ENTRY_CONDITION',
                                                                name: 'immigrant_entry_condition',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.immigrant_entry_condition_diff : false)
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
                                                                name: 'immigrant_entry_condition_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.immigrant_entry_condition_diff : false)
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
                                                                fieldLabel: 'RIC',
                                                                xtype: 'textfield',
                                                                width: 260,
                                                                readOnly: true,
                                                                enableKeyEvents: true,
                                                                name: 'ric',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.ric_diff : false)
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
                                                                name: 'ric_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.ric_diff : false)
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
                                                                fieldLabel: 'RIC - Órgão emissor',
                                                                xtype: 'textfield',
                                                                name: 'ric_issuer',
                                                                enableKeyEvents: true,
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.ric_issuer_diff : false)
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
                                                                name: 'ric_issuer_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.ric_issuer_diff : false)
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
                                                                name: 'ric_expedition_date',
                                                                fieldLabel: 'RIC - Data de Expedição',
                                                                xtype: 'datefield',
                                                                allowBlank: true,
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.ric_expedition_date_diff : false)
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
                                                                name: 'ric_expedition_date_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.ric_expedition_date_diff : false)
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
                                                                xtype: 'rest-autocompletefield',
                                                                fieldLabel: 'RIC - UF',
                                                                name: 'ric_state',
                                                                displayField: 'unicode',
                                                                allowBlank: true,
                                                                rest: 'rh.estado.Restful',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.ric_state_diff : false)
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
                                                                name: 'ric_state_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.ric_state_diff : false)
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
                                                                fieldLabel: 'RNE',
                                                                xtype: 'textfield',
                                                                width: 260,
                                                                readOnly: true,
                                                                enableKeyEvents: true,
                                                                name: 'rne',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.rne_diff : false)
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
                                                                name: 'rne_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.rne_diff : false)
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
                                                                fieldLabel: 'RNE - Órgão emissor',
                                                                xtype: 'textfield',
                                                                name: 'rne_issuer',
                                                                enableKeyEvents: true,
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.rne_issuer_diff : false)
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
                                                                name: 'rne_issuer_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.rne_issuer_diff : false)
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
                                                                name: 'rne_expedition_date',
                                                                fieldLabel: 'RNE - Data de Expedição',
                                                                xtype: 'datefield',
                                                                allowBlank: true,
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.rne_expedition_date_diff : false)
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
                                                                name: 'rne_expedition_date_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.rne_expedition_date_diff : false)
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
                                                                xtype: 'rest-autocompletefield',
                                                                fieldLabel: 'RNE - UF',
                                                                name: 'rne_state',
                                                                displayField: 'unicode',
                                                                allowBlank: true,
                                                                rest: 'rh.estado.Restful',
                                                                width: 260,
                                                                readOnly: true,
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.rne_state_diff : false)
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
                                                                name: 'rne_state_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.rne_state_diff : false)
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
                                                                fieldLabel: 'NIS',
                                                                xtype: 'textfield',
                                                                width: 260,
                                                                readOnly: true,
                                                                enableKeyEvents: true,
                                                                name: 'nis',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.nis_diff : false)
                                                            }
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
                                                                name: 'nis_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.nis_diff : false)
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
                                                            this.getFotoField(cfg)
                                                        ]
                                                },
                                                {
                                                    layout: 'form',
                                                    region: 'center',
                                                    border: false,
                                                    style: 'margin-left: 5px',
                                                    hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.foto_diff : false),
                                                    items:
                                                        [
                                                            this.getPanelFoto(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.foto_link : null)
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
                                                                name: 'foto_valid_',
                                                                width: 15,
                                                                style: 'margin-left: -45px',
                                                                hidden: this.trueOrFalse(cfg.selecteDataGridFormInformation ? cfg.selecteDataGridFormInformation.foto_diff : false)
                                                            }
                                                        ]
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
                            width: '400',
                            style: 'margin-left: 5px',
                            items: [
                                {
                                    xtype: 'fieldset',
                                    title: 'Documentos Digitais',
                                    name: 'fieldServidor',
                                    width: '400',
                                    items: [
                                        this.getFormGed()
                                    ]
                                },
                                this.tabDependent(cfg)
                            ]
                        }
                    ]
                }]
            });
        }
        return this._formPanel;
    },
});

