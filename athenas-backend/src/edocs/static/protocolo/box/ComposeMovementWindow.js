Ext._define('edocs.protocolo.box.ComposeMovementWindow', {
    extend: 'Ext.Window',

    width: 900,

    getUrgencyField: function (cfg) {
        if (!this._urgencyField) {
            this._urgencyField = Ext._create('Ext.form.Checkbox', {
                name: 'urgency',
                hideLabel: true,
                boxLabel: 'Pedir urgência'
            });
        }

        return this._urgencyField;
    },

    getAdviceField: function (cfg) {
        if (!this._adviceField) {
            this._adviceField = Ext._create('toolkit.fields.CKEditor', {
                name: 'advice',
                height: 430
            });
        }

        return this._adviceField;
    },

    getAdvicePanel: function(cfg) {
        cfg = (cfg || {});

        if(!this._advicePanel)
            this._advicePanel = Ext._create('Ext.Panel', {
                title: 'Parecer',
                border: false,
                scope: this,
                items: [
                    {
                        xtype: 'panel',
                        frame: true,
                        border: false,
                        layout: 'column',
                        defaults: {
                            border: false,
                            layout: 'form',
                        },
                        scope: this,
                        items: [
                            {
                                columnWidth: 0.30,
                                items: this.getUrgencyField(cfg)
                            },
                            {
                                columnWidth: 0.53,
                                labelWidth: 90,
                                items: this.getControlTypeField(cfg)
                            },
                            {
                                columnWidth: 0.17,
                                items: this.getAllowedListButton(cfg)
                            }
                        ],
                    },
                    this.getAdviceField(cfg)
                ]
            });

        return this._advicePanel;
    },

    getAttachmentGrid: function(cfg) {
        if(!this._attachmentGrid) {
            this._attachmentGrid = Ext._create('edocs.protocolo.AttachmentGrid', {
                title: 'Anexos',
                driver: 'local',
                gridAutoLoad: false
            });

            this._attachmentGrid.setParam('moviment', 0);
            this._attachmentGrid.setFilterProperty('moviment', 0, 100, false);
        }

        return this._attachmentGrid;
    },

    getReferenceGrid: function(cfg) {
        if(!this._referenceGrid) {
            this._referenceGrid = Ext._create('edocs.protocolo.ReferenciaGrid', {
                title: 'Referencias',
                driver: 'local',
                gridAutoLoad: false
            });

            this._referenceGrid.setParam('movimentacao', 0);
            this._referenceGrid.setFilterProperty('movimentacao', 0, 100, false);
        }

        return this._referenceGrid;
    },

    getTabPanel: function(cfg) {
        if(!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                height: 600,
                activeTab: 0,
                // deferredRender: false,
                items: [
                    this.getDestinationPanel(cfg),
                    this.getAdvicePanel(cfg),
                    this.getAttachmentGrid(cfg),
                    this.getReferenceGrid(cfg)
                ],
                listeners: {
                    scope: this,
                    render: function(panel) {
                        panel.activate(this.getAdvicePanel());
                        panel.activate(this.getAttachmentGrid());
                        panel.activate(this.getReferenceGrid());
                        panel.activate(this.getDestinationPanel());
                    }
                }
            });

        return this._tabPanel;
    },

    getPersonDestinationGrid: function() {
        if(!this._personDestinationGrid)
            this._personDestinationGrid = Ext._create('edocs.protocolo.box.PersonDestinationGrid', {
                title: 'Enviar para as PESSOAS',
                flex: 1
            });

        return this._personDestinationGrid;
    },

    getGroupPersonDestinationGrid: function() {
        if(!this._groupPersonDestinationGrid)
            this._groupPersonDestinationGrid = Ext._create('edocs.protocolo.box.GroupPersonDestinationGrid', {
                title: 'Enviar para Grupo de PESSOAS',
                flex: 1
            });

        return this._groupPersonDestinationGrid;
    },

    getLocationDestinationGrid: function() {
        if(!this._locationDestinationGrid)
            this._locationDestinationGrid = Ext._create('edocs.protocolo.box.LocationDestinationGrid', {
                title: 'Enviar para as LOTAÇÕES',
                flex: 1
            });

        return this._locationDestinationGrid;
    },

    getGroupLocationDestinationGrid: function() {
        if(!this._groupLocationDestinationGrid)
            this._groupLocationDestinationGrid = Ext._create('edocs.protocolo.box.GroupLocationDestinationGrid', {
                title: 'Enviar para Grupo de LOTAÇÕES',
                flex: 1
            });

        return this._groupLocationDestinationGrid;
    },

    getDestinationLocationPanel: function(cfg) {
        if(!this._destinationLocationPanel)
            this._destinationLocationPanel = Ext._create('Ext.TabPanel', {
                activeTab: 0,
                border: false,
                flex: 1.0,
                tabPosition: 'bottom',
                items: [
                    {
                        xtype: 'panel',
                        title: 'Individual',
                        border: false,
                        layout: 'fit',
                        items: [
                            this.getLocationDestinationGrid()
                        ]
                    },
                    {
                        xtype: 'panel',
                        title: 'Grupo',
                        border: false,
                        layout: 'fit',
                        items: [
                            this.getGroupLocationDestinationGrid()
                        ]
                    }
                ]
            });

        return this._destinationLocationPanel;
    },

    getDestinationPersonPanel: function(cfg) {
        if(!this._destinationPersonPanel)
            this._destinationPersonPanel = Ext._create('Ext.TabPanel', {
                activeTab: 0,
                border: false,
                flex: 1.0,
                tabPosition: 'bottom',
                items: [
                    {
                        xtype: 'panel',
                        title: 'Individual',
                        border: false,
                        layout: 'fit',
                        items: [
                            this.getPersonDestinationGrid()
                        ]
                    },
                    {
                        xtype: 'panel',
                        title: 'Grupo',
                        border: false,
                        layout: 'fit',
                        items: [
                            this.getGroupPersonDestinationGrid()
                        ]
                    }
                ]
            });

        return this._destinationPersonPanel;
    },

    getDispatchTypePanel: function() {
        if(!this._dispatchTypePanel)
            this._dispatchTypePanel = Ext._create('Ext.Panel', {
                xtype: 'panel',
                frame: true,
                border: false,
                layout: {
                    type: 'hbox',
                    align: 'stretch'
                },
                defaults: { flex: 1.0 },
                height: 35,
                items: [
                    this.getDispatchTypeField()
                ]
            });
        return this._dispatchTypePanel;
    },

    getDispatchTypeField: function() {
        if(!this._dispatchTypeField) {
            this._dispatchTypeField = Ext._create('Ext.form.RadioGroup', {
                xtype: 'radiogroup',
                allowBlank: false,
                items: [
                    {
                        boxLabel: 'Enviar apenas por meio eletrônico',
                        name: 'physical',
                        inputValue: false,
                        checked: true
                    },
                    {
                        boxLabel: 'Enviar por meio físico e eletrônico',
                        name: 'physical',
                        inputValue: true
                    },
                ]
            });
        }
        return this._dispatchTypeField;
    },

    getDestinationPanel: function(cfg) {
        if(!this._destinationPanel)
            this._destinationPanel = Ext._create('Ext.Panel', {
                title: 'Destinatários',
                layout: {
                    type: 'vbox',
                    align: 'stretch'
                },
                items: [
                    this.getDispatchTypePanel(),
                    this.getDestinationLocationPanel(),
                    this.getDestinationPersonPanel()
                ]
            });

        return this._destinationPanel;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: [
                    {
                        xtype: 'checkbox',
                        name: 'opinion',
                        boxLabel: 'Assinar Eletronicamente',
                        hidden: true,
                        checked: true
                    },
                    this.getTabPanel(cfg)
                ]
            });

        return this._formPanel;
    },

    send: function(params) {
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Movimentando...'});
        mask.show();

        Ext.Ajax.request({
            url: core.callAction('EDOCManage', 'send'),
            scope: this,
            params: params,
            callback: function() { mask.hide(); },
            success: function(xhr) {
                var result = Ext.decode(xhr.responseText);

                if (result.success) {
                    core.invokeCallback((this.success || {fn: Ext.emptyFn}), result);
                    this.close();
                } else {
                    Ext.Msg.show({
                        title: 'Movimentando',
                        msg: result.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            failure: function() {
                Ext.Msg.show({
                    title: 'Movimentando',
                    msg: 'Recurso indisponível no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            },
        });
    },

    validateFields: function () {
        function showError(msg) {
            Ext.Msg.show({
                title: 'Validando',
                msg: msg,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                minWidth: 400,
            });
            throw msg;
        }

        if (!this.getDispatchTypeField().isValid(true)) {
            showError('Informe se o envio do documento será por meio eletrônico e/ou por meio físico');
        }

        if (this.getPersonDestinationGrid().selected.length === 0
                && this.getLocationDestinationGrid().selected.length === 0
                && this.getGroupPersonDestinationGrid().selected.length === 0
                && this.getGroupLocationDestinationGrid().selected.length === 0) {
            showError('Selecione pelo menos um destinatário para a movimentação do documento.');
        }
    },

    getParams: function (cfg) {
        var params = this.getFormPanel().getForm().getValues();

        params.person_destination = this.getPersonDestinationGrid().selected;
        params.location_destination = this.getLocationDestinationGrid().selected;
        params.group_person = this.getGroupPersonDestinationGrid().selected;
        params.group_location = this.getGroupLocationDestinationGrid().selected;

        params.attachments = {};
        params.references = {};
        params.movement = this.movement;

        params.urgency = (!params.urgency ? 'off' : params.urgency);
        params.close = (!params.close ? 'off' : params.close);
        params.opinion = (!params.opinion ? 'off' : params.opinion);

        function prepareOperation(store) {
            var field = { create: [], update: [], delete: [] };

            store.each(function(data) {
                var operation = data.get('operation');

                if(operation === 'C')
                    field.create.push(data.data);
                else if(operation === 'U')
                    field.update.push(data.data);
                else if(operation === 'D')
                    field.update.push(data.get('pk'));
                else
                    console.warn('Unknow operation %s', operation);
            });

            return Ext.encode(field);
        }

        params.attachments = prepareOperation(this.getAttachmentGrid().getStore());
        params.references = prepareOperation(this.getReferenceGrid().getStore());

        return params;
    },

    accessControl: function (params) {
        var mask = new Ext.LoadMask(
            this.getEl(),
            {msg: 'Classificando informação...'}
        );
        mask.show();

        Ext.Ajax.request({
            url: core.callAction('EDOCManage', 'access_control'),
            scope: this,
            params: params,
            callback: function () {
                mask.hide();
            },
            success: function (xhr) {
                var result = Ext.decode(xhr.responseText);

                if (result.success) {
                    core.invokeCallback((this.success || {fn: Ext.emptyFn}), result);
                    this.send(this.getParams());
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

    hasControlTypeChanged: function (cfg) {
        var controlType = this.getControlTypeField().getValue();
        return (this.getControlTypeField().wasChanged() && controlType);
    },

    showJustificationWindow: function (cfg) {
        var controlType = this.getControlTypeField().getValue();

        Ext._create('common.document_access.JustificationWindow', {
            title: 'Classificação de informação',
            scope: this,
            controlType: controlType,
            showDialogWhenCanceling: true,
            handler: function (justification, legalPrerogative) {
                this.accessControl({
                    movement: this.movement,
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

    getMovementButton: function (cfg) {
        if (!this._movementButton) {
            this._movementButton = Ext._create('Ext.Button', {
                text: 'Movimentar',
                scope: this,
                handler: function () {
                    this.validateFields();

                    if (this.hasControlTypeChanged(cfg)) {
                        this.showJustificationWindow(cfg);
                    } else {
                        this.send(this.getParams(cfg));
                    }
                }
            });
        }

        return this._movementButton;
    },

    getControlTypeField: function (cfg) {
        if (!this._controlTypeField) {
            var self = this;

            this._controlTypeField = Ext._create('core.fields.ComboField', {
                name: 'control_type',
                submitValue: false,
                fieldLabel: 'Nível de acesso',
                emptyText: 'Deixe em branco para classificar como público',
                allowBlank: true,
                displayField: 'title',
                value: (cfg || {}).controlType || 0,
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

            // Força a exibição do Nível de Acesso, mesmo que 
            // o usuário não tenha permissão para usá-lo.
            // Ver implementação da action get_query no 
            // controller DAControlTypeByUser.
            this._controlTypeField.store.baseParams = {
                control_type: (cfg || {}).controlType || 0
            };

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

    showAllowedListWindow: function (cfg) {
        Ext._create('common.document_access.allowedlistitem.Modal', {
            control: cfg.control || 0,
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
                disabled: (cfg.isSecret ? false : true),
                handler: function() {
                    this.showAllowedListWindow(cfg);
                }
            });
        }

        return this._allowedListButton;
    },

    getCancelButton: function (cfg) {
        if (!this._cancelButton) {
            this._cancelButton = Ext._create('Ext.Button', {
                text: 'Cancelar',
                scope: this,
                handler: this.close
            });
        }

        return this._cancelButton;
    },

    getButtons: function (cfg) {
        if (!this._buttons) {
            this._buttons = [
                this.getMovementButton(cfg),
                this.getCancelButton(cfg)
            ];
        }

        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Movimentação de Protocolo',
            modal: true,
        });

        Ext.apply(cfg, {
            resizable: false,
            border: false,
            items: this.getFormPanel(cfg),
            buttons: this.getButtons(cfg)
        });

        edocs.protocolo.box.ComposeMovementWindow.superclass.constructor.call(this, cfg);
    }
});
