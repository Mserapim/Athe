Ext._define('edocs.protocolo.box.ComposeWindow', {
    extend: 'Ext.Window',

    width: 900,

    _resource: 'EDOCManage',

    _moveButtonWasClicked: false,

    getCodeField: function (cfg) {
        if (!this._codeField) {
            this._codeField = Ext._create('Ext.form.DisplayField', {
                name: 'code',
                fieldLabel: 'Código',
                //style: { fontWeight: 'bold' },
            });
        }

        return this._codeField;
    },

    getHomeCourtField: function (cfg) {
        if (!this._homeCourtField) {
            this._homeCourtField = Ext._create('core.fields.ComboField', {
                fieldLabel: 'Origem',
                hiddenName: 'home_court',
                displayField: 'description',
                // emptyText: 'Origem do documento.',
                store: Ext._create('Ext.data.Store', {
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction(this._resource, 'work_locations')
                    }),
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            { name: 'pk', type: 'int' },
                            { name: 'description', type: 'string' },
                        ]
                    })
                }),
                width: 485,
                allowBlank: false
            });
        }

        return this._homeCourtField;
    },

    getTipoDocumentoField: function (cfg) {
        if (!this._tipoDocumentoField) {
            this._tipoDocumentoField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Tipo',
                name: 'document_type',
                resizable: true,
                rest: 'edocs.protocolo.TipoDocumentoRestful',
                width: 210,
                preFilter: this.getTipoDocumentoFilter(),
                allowBlank: false,
                readOnly: ((cfg || {}).tipoDocumentoReadyOnly || false)
            });
        }

        return this._tipoDocumentoField;
    },

    getSubjectField: function (cfg, config) {
        if (!this._subjectField) {
            this._subjectField = Ext._create('Ext.form.TextField', Ext.apply(
                {
                    fieldLabel: 'Assunto',
                    name: 'subject',
                    anchor: '99%',
                    //emptyText: 'Assunto tratado no documento',
                },
                config || {}
            ));
        }

        return this._subjectField;
    },

    getExternalNumberField: function (cfg) {
        if (!this._externalField) {
            this._externalField = Ext._create('Ext.form.CompositeField', {
                items: [
                    {
                        fieldLabel: 'Número Externo',
                        name: 'external_number',
                        xtype: 'textfield',
                        // emptyText: 'Se houver um número de protocolo externo',
                        width: 599
                    }
                ]
            });
        }

        return this._externalField;
    },

    getMovementButton: function (cfg) {
        if (!this._movimentButton) {
            this._movimentButton = Ext._create('Ext.Button', {
                text: 'Movimentar',
                scope: this,
                handler: this.moveProtocol
            });
        }

        return this._movimentButton;
    },

    getSignButton: function (cfg) {
        if (!this._signButton) {
            this._signButton = Ext._create('Ext.Button', {
                text: 'Assinar',
                scope: this,
                handler: this.signDocument
            });
        }

        return this._signButton;
    },

    getSaveButton: function (cfg) {
        if (!this._saveButton) {
            this._saveButton = Ext._create('Ext.Button', {
                text: 'Salvar modificações',
                scope: this,
                handler: this.checkSignature
            });
        }

        return this._saveButton;
    },

    moveProtocol: function () {
        this._moveButtonWasClicked = true;

        var values = this.getFormPanel().getForm().getValues();
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Protocolizando o documento...' });

        values.movement_id = this.movement();

        mask.show();
        Ext.Ajax.request({
            url: core.callAction(this._resource, 'docketing'),
            scope: this,
            params: values,
            callback: function () {
                mask.hide();
            },
            success: function (xhr) {
                var result = Ext.decode(xhr.responseText);

                if (result.success) {
                    core.invokeCallback((this.success || { fn: function () {} }));
                    this.readProtocolInstance(result.instance);

                    if (this.hasControlTypeChanged()) {
                        this.showJustificationWindow();
                    } else {
                        this.values = this.values || {};
                        this.showMovementWindow({
                            movement: this.movement(),
                            control: this.values.control || 0,
                            controlType: this.values.control_type || 0,
                            legalPrerogative: this.values.legal_prerogative || 0,
                            isCommitted: this.values.is_committed || false,
                            isSecret: this.values.is_secret || false,
                            success: this.success,
                        });
                    }
                } else {
                    Ext.Msg.show({
                        title: 'Protocolizando o documento',
                        msg: result.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            failure: function () {
                Ext.Msg.show({
                    title: 'Protocolizando o documento...',
                    msg: 'Recurso indisponível no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    signDocument: function () {
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Assinando o documento...' });
        mask.show();

        Ext.Ajax.request({
            url: core.callAction(this._resource, 'sign_document'),
            params: {
                pkset: this.movement()
            },
            scope: this,
            callback: function () {
                mask.hide();
            },
            success: function (xhr) {
                var result = Ext.decode(xhr.responseText);

                if (result.success) {
                    core.invokeCallback((this.success || { fn: function () {} }));
                }
                else
                    Ext.Msg.show({
                        title: 'Assinando documento',
                        msg: result.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function () {
                Ext.Msg.show({
                    title: 'Assinando documento',
                    msg: 'Recurso indisponível no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    checkSignature: function () {
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Verificando assinatura...' });
        mask.show();

        Ext.Ajax.request({
            url: core.callAction(this._resource, 'status_signature_document'),
            params: {
                pkset: this.movement()
            },
            scope: this,
            callback: function () {
                mask.hide();
            },
            success: function (xhr) {
                var result = Ext.decode(xhr.responseText);

                if (result.signature) {
                    Ext.Msg.show({
                        title: 'Verificando assinatura',
                        msg: 'Você está modificando um documento assinado. Se salvá-lo as assinaturas serão perdidas, sendo necessário assiná-lo novamente. Deseja continuar?',
                        icon: Ext.Msg.QUESTION,
                        buttons: Ext.Msg.YESNO,
                        scope: this,
                        fn: function (btn) {
                            if (btn == 'no') {
                                return;
                            }
                            this.saveProtocol();
                        }
                    });
                } else {
                    this.saveProtocol();
                }
            },
            failure: function () {
                Ext.Msg.show({
                    title: 'Assinando documento',
                    msg: 'Recurso indisponível no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    saveProtocol: function () {
        var values = this.getFormPanel().getForm().getValues();
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Protocolizando o documento...' });

        if (this.movement()) values.movement_id = this.movement();

        mask.show();
        Ext.Ajax.request({
            url: core.callAction(this._resource, 'docketing'),
            scope: this,
            params: values,
            callback: function () {
                mask.hide();
            },
            success: function (xhr) {
                var result = Ext.decode(xhr.responseText);

                if (result.success) {
                    core.invokeCallback((this.success || { fn: function () {} }));
                    this.readProtocolInstance(result.instance);

                    if (this.hasControlTypeChanged()) {
                        this.showJustificationWindow();
                    }
                } else {
                    Ext.Msg.show({
                        title: 'Protocolizando o documento',
                        msg: result.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            failure: function () {
                Ext.Msg.show({
                    title: 'Protocolizando o documento...',
                    msg: 'Recurso indisponível no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    accessControl: function (params) {
        var mask = new Ext.LoadMask(
            this.getEl(),
            {msg: 'Classificando o documento...'}
        );
        mask.show();

        Ext.Ajax.request({
            url: core.callAction(this._resource, 'access_control'),
            scope: this,
            params: params,
            callback: function () {
                mask.hide();
            },
            success: function (xhr) {
                var result = Ext.decode(xhr.responseText);

                if (result.success) {
                    core.invokeCallback((this.success || { fn: function () {} }));

                    this.values = this.values || {};
                    this.values.control_type = this.getControlTypeField().getValue();
                    this.values.is_secret = result.instance.is_secret;

                    if (result.instance.is_secret) {
                        this.getAllowedListButton().enable();
                    } else {
                        this.getAllowedListButton().disable();
                    }

                    if (this._moveButtonWasClicked) {
                        this.showMovementWindow({
                            movement: this.movement(),
                            control: result.instance.control,
                            controlType: result.instance.control_type,
                            legalPrerogative: result.instance.legal_prerogative,
                            isCommitted: result.instance.is_committed,
                            isSecret: result.instance.is_secret,
                            success: this.success,
                        });
                    }
                } else {
                    this.getControlTypeField().undoChange();

                    Ext.Msg.show({
                        title: 'Classificando informação',
                        msg: result.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            failure: function () {
                this.getControlTypeField().undoChange();

                Ext.Msg.show({
                    title: 'Classificando informação',
                    msg: 'Recurso indisponível no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    hasControlTypeChanged: function () {
        var controlType = this.getControlTypeField().getValue();
        return (this.getControlTypeField().wasChanged() && controlType);
    },

    showJustificationWindow: function () {
        var controlType = this.getControlTypeField().getValue();

        Ext._create('common.document_access.JustificationWindow', {
            title: 'Classificação de informação',
            scope: this,
            controlType: controlType,
            showDialogWhenCanceling: true,
            handler: function (justification, legalPrerogative) {
                this.accessControl({
                    movement: this.movement(),
                    control_type: controlType,
                    legal_prerogative: legalPrerogative,
                    justification: justification,
                    is_committed: 'off',  // Cria um controle de acesso "sem compromisso", isto é, pendente de classificação.
                });
            },
            failure: function (error) {
                this.getControlTypeField().undoChange();
            }
        }).show();
    },

    showMovementWindow: function (config) {
        Ext._create('edocs.protocolo.box.ComposeMovementWindow', {
            movement: (config.movement !== undefined ? config.movement : 0),
            control: (config.control !== undefined ? config.control : 0),
            controlType: (config.controlType !== undefined ? config.controlType : 0),
            legalPrerogative: (config.legalPrerogative !== undefined ? config.legalPrerogative : 0),
            isCommitted: (config.isCommitted !== undefined ? config.isCommitted : false),
            isSecret: (config.isSecret !== undefined ? config.isSecret : false),
            success: config.success,
        }).show();

        this.close();
    },

    /*
     * Este campo lista os tipos de controles que usuário poderá
     * utilizar para classificar ou reclassificar o controle de
     * acesso de um atendimento.
     *
     * Como não é um campo original do modelo Attendance, ele
     * está sendo configurado para não submeter seu valor.
     */
    getControlTypeField: function (cfg) {
        if (!this._controlTypeField) {
            var self = this;

            this._controlTypeField = Ext._create('core.fields.ComboField', {
                name: 'control_type',
                submitValue: false,  // Não submeter.
                fieldLabel: 'Nível de acesso',
                emptyText: 'Deixe em branco para classificar como público',
                allowBlank: true,
                displayField: 'title',
                rest: 'common.document_access.controltype.byUser.Restful',
                anchor: '98%',
                listeners: {
                    scope: this,
                    change: function(field, newValue, oldValue) {
                        this._controlTypeField._newValue = newValue;
                        this._controlTypeField._oldValue = oldValue;
                    }
                }
            });

            this._controlTypeField.getStore().on({
                load: function (store) {
                    store.insert(
                        0,
                        Ext._create('Ext.data.Record', {
                            pk: 0,
                            title: 'Público',
                            unicode: 'Público'
                        })
                    );
                }
            });

            /**
             * Desfaz a última mudança do valor do ComboBox.
             */
            this._controlTypeField.undoChange = function () {
                if (self._controlTypeField._oldValue !== undefined) {
                    self._controlTypeField.setValue(self._controlTypeField._oldValue);
                }
            }

            /**
             * Verifica se houve mudança no valor do ComboBox.
             * @return {boolean} Retorna true uma vez para cada mudança.
             */
            this._controlTypeField.wasChanged = function () {
                var result = (self._controlTypeField._oldValue !== self._controlTypeField._newValue);
                self._controlTypeField._newValue = self._controlTypeField._oldValue;
                return result;
            }
        }

        return this._controlTypeField;
    },

    showAllowedListWindow: function(cfg) {
        Ext._create('common.document_access.allowedlistitem.Modal', {
            control: ((cfg || {}).values || {}).control || 0,
            title: 'Credenciais de acesso',
            gridConfig: {
                allowUpdate: false,
                allowRemove: false,
                columnAction: false,
            }
        }).show();
    },

    getAllowedListButton: function (cfg) {
        if (!this._allowedListButton) {
            this._allowedListButton = Ext._create('Ext.Button', {
                text: 'Credenciais de acesso',
                width: 145,
                iconCls: 'icon-document_access icon-document_access-allowedlist',
                scope: this,
                disabled: (((cfg || {}).values || {}).is_secret ? false : true),
                handler: function() {
                    this.showAllowedListWindow(cfg);
                }
            });
        }

        return this._allowedListButton;
    },

    getControlContainer: function (cfg) {
        return {
            xtype: 'container',
            layout: 'hbox',
            items: [
                {
                    xtype: 'container',
                    flex: 0.82,
                    layout: 'form',
                    items: this.getControlTypeField(cfg),
                },
                {
                    xtype: 'container',
                    flex: 0.18,
                    items: this.getAllowedListButton(cfg),
                }
            ]
        };
    },

    readProtocolInstance: function (instance) {
        this.getFormPanel().getForm().setValues(instance);
        this.protocol = instance.protocol;
        this.movement(instance.pk);
    },

    movement: function (value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if (value !== undefined) {
            this._movement = value;

            if (dispatch)
                this.observeMovement();
        }

        return this._movement;
    },

    observeMovement: function () {
        var value = this.movement();
        var grid;


        if (value) {
            grid = this.getAttachmentPanel();
            grid.enable();
            grid.setParam('moviment', value);
            grid.setFilterProperty('moviment', value, 100);

            grid = this.getReferencePanel();
            grid.enable();
            grid.setParam('movimentacao', value);
            grid.setFilterProperty('movimentacao', value, 100);

            this.getMovementButton().enable();
            this.getSignButton().enable();
        }
        else {
            grid = this.getAttachmentPanel();
            grid.disable();
            grid.setParam('moviment', value);
            grid.setFilterProperty('moviment', value, 100, false);
            grid.getStore().removeAll();

            grid = this.getReferencePanel();
            grid.disable();
            grid.setParam('movimentacao', value);
            grid.setFilterProperty('movimentacao', value, 100, false);
            grid.getStore().removeAll();

            this.getMovementButton().disable();
            this.getSignButton().disable();

        }
    },

    getInformationPanel: function (cfg) {
        if (!this._informationPanel) {
            this._informationPanel = Ext._create('Ext.Panel', {
                title: 'Informações',
                items: [
                    this.getMainPanel(cfg),
                    this.getComplementePanel()
                ]
            });
        }

        return this._informationPanel;
    },

    getComplementePanel: function (cfg) {
        if (!this._complementPanel) {
            this._complementPanel = Ext._create('Ext.Panel', {
                layout: {
                    type: 'vbox',
                    align: 'stretch'
                },
                border: false,
                height: 428,
                items: [
                    this.getAttachmentPanel(),
                    this.getReferencePanel()
                ]
            });
        }

        return this._complementPanel;
    },

    getAttachmentPanel: function (cfg) {
        if (!this._attachmentPanel) {
            this._attachmentPanel = Ext._create('edocs.protocolo.AttachmentGrid', {
                title: 'Anexos',
                flex: 1,
                gridAutoLoad: false,
                columnAction: false
            });
        }

        return this._attachmentPanel;
    },

    getReferencePanel: function (cfg) {
        if (!this._referencePanel) {
            this._referencePanel = Ext._create('edocs.protocolo.ReferenciaGrid', {
                title: 'Referências',
                flex: 1,
                gridAutoLoad: false,
                columnAction: false
            });
        }

        return this._referencePanel;
    },

    __getSecondLineMainPanel: function (cfg) {
        if (!this.__secondLineMainPanel) {
            this.__secondLineMainPanel = Ext.create('Ext.Container');
        }

        return this.__secondLineMainPanel;
    },

    getTipoDocumentoFilter: function () {
        return [
            { property: 'habilita', value: 'on', stage: 1 }
        ];
    },

    getMainPanel: function (cfg) {
        if (!this._mainPanel) {
            this._mainPanel = Ext._create('Ext.Panel', {
                frame: true,
                layout: 'form',
                items: [
                    this.getCodeField(cfg),
                    {
                        xtype: 'container',
                        layout: 'hbox',
                        anchor: '99%',
                        items: [
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 2.75,
                                items: [
                                    this.getHomeCourtField(cfg)
                                ]
                            },
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 1.25,
                                labelWidth: 50,
                                items: [
                                    this.getTipoDocumentoField()
                                ]
                            }
                        ]
                    },
                    this.getSubjectField(cfg),
                    this.getExternalNumberField(),
                    this.getControlContainer(cfg),
                ]
            });
        }

        return this._mainPanel;
    },

    getContentPanel: function (cfg) {
        if (!this._contentPanel) {
            this._contentPanel = Ext._create('Ext.Panel', {
                title: 'Conteúdo',
                items: [
                    {
                        xtype: 'ckeditor',
                        name: 'content',
                        height: 444
                    }
                ]
            });
        }

        return this._contentPanel;
    },

    getTabPanel: function (cfg) {
        if (!this._tabPanel) {
            this._tabPanel = Ext._create('Ext.TabPanel', {
                activeTab: 0,
                height: 574,
                border: false,
                deferredRender: false,
                items: [
                    this.getInformationPanel(cfg),
                    this.getContentPanel()
                ]
            });
        }

        return this._tabPanel;
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: [ this.getTabPanel(cfg) ]
            });
        }

        return this._formPanel;
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Editor de Protocolo'
            }
        );

        Ext.apply(
            cfg,
            {
                resizable: false,
                border: false,
                buttonAlign: 'left',
                buttons: [
                    this.getMovementButton(),
                    this.getSignButton(),
                    '->',
                    this.getSaveButton(),
                    {
                        text: 'Fechar',
                        scope: this,
                        handler: function () { this.close(); }
                    }
                ],
                items: this.getFormPanel(cfg)
            }
        );

        edocs.protocolo.box.ComposeWindow.superclass.constructor.call(this, cfg);

        if (cfg.objectId) {
            this.movement(cfg.objectId);
        }

        this.on({
            scope: this,
            afterrender: function () {
                if (!this.objectId)
                    this.observeMovement();
                else
                    this.movement(this.objectId);
            },
            render: function () {
                if (this.values) {
                    this.getFormPanel().getForm().setValues(this.values);
                }
            }
        });
    }
});
