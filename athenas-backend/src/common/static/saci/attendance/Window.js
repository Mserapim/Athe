Ext._define('common.saci.attendance.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.saci.attendance.Restful',

    width: 900,
    height: 600,

    loadAttachment: function(value) {
        if(value) {
            this.getAttachmentGrid().enable();
            this.getAttachmentGrid().setParam('attendance', value);
            this.getAttachmentGrid().setFilterProperty('attendance', value, 100);
        } else {
            this.getAttachmentGrid().disable();
            this.getAttachmentGrid().setParam('attendance', 0);
            this.getAttachmentGrid().setFilterProperty('attendance', 0, 100);
        }
    },

    getRepresentedField: function(cfg){
        if(!this._representedField){
            this._representedField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Representado",
                allowBlank: true,
                rest: "rh.person.Restful",
                name: "represented",
                disabled: true,
            });
        }

        return this._representedField;
    },

    _isCheckedRepresented: function(cfg, checked){
        if(checked)
            this.getRepresentedField().enable();
        else{
            this.getRepresentedField().disable();
        }

        this.getRepresentedField().setValue('');
        this.getRepresentedField().getComboField().getStore().removeAll();
    },

    getTabFeedbackField: function(cfg) {
        if(!this._tabFeedbackField)
            this._tabFeedbackField = Ext._create('Ext.Panel',{
                layout: 'form',
                title: 'Parecer',
                border: false,
                frame: false,
                scope: this,
                autoHeight: true,
                disabled: true,
                items: [
                    {
                        allowBlank: true,
                        fieldLabel: "Parecer",
                        name: "feedback",
                        xtype: "ckeditor",
                        hideLabel: true,
                        height: 180,
                        submit: true,
                    }
                ]
            });
        return this._tabFeedbackField;
    },

    getStoryPanel: function(cfg) {
        if(!this._storyPanel)
            this._storyPanel = Ext._create('Ext.Panel',{
                layout: 'form',
                title: 'Relato do Cidadão',
                border: true,
                frame: false,
                scope: this,
                items: [
                    {
                        allowBlank: true,
                        fieldLabel: "Relato",
                        name: "story",
                        xtype: "ckeditor",
                        hideLabel: true,
                        height: 200,
                        submit: true,
                    }
                ]
            });
        return this._storyPanel;
    },

    getDepartmentField: function(cfg) {
        if(!this._departmentField){
            this._departmentField = Ext._create('core.fields.ComboField', {
                fieldLabel: 'Atuando por',
                hiddenName: 'department',
                displayField: 'description',
                store: Ext._create('Ext.data.Store', {
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('EDOCManage', 'work_locations')
                    }),
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            {name: 'pk', type: 'int'},
                            {name: 'description', type: 'string'},
                        ]
                    })
                }),
                width: 767,
                allowBlank: false
            });
        }

        return this._departmentField;
    },

    getTypologyField: function(cfg) {
        if(!this._typologyField)
            this._typologyField = Ext._create('core.fields.AutocompleteField',{
                xtype: "rest-autocompletefield",
                fieldLabel: "Público Alvo",
                allowBlank: false,
                rest: "common.saci.typology.Restful",
                name: "typology",
            });
        return this._typologyField;
    },

    getItemsMainPanel: function(cfg) {
        return [
            this.getDepartmentField(),
            this.getTypologyField(),
            {
                allowBlank: false,
                fieldLabel: "Assunto",
                name: "subject",
                xtype: "textfield",
                width: 767,

            },
            {
                xtype: 'checkbox',
                boxLabel: 'O Cidadão representa alguém?',
                labelSeparator: '&nbsp;',
                fieldLabel: '&nbsp;',
                allowBlank: true,
                name: 'contains_represented',
                listeners: {
                    scope: this,
                    check: this._isCheckedRepresented
                }
            },
            this.getRepresentedField(cfg),
            this.getControlContainer(cfg),
            this.getStoryPanel()
        ];
    },

    getAttachmentGrid: function(cfg) {
        if(!this._attachmentGrid)
            this._attachmentGrid = Ext._create('common.saci.attachment.Grid', {
                title: 'Anexos',
                gridAutoLoad: false,
                columnAction: false,
                height: 510,
                disabled: true
            });

        return this._attachmentGrid;
    },

    getMainPanel: function(cfg){
        if(!this._mainTab)
            this._mainTab = Ext._create('Ext.Panel',{
                layout: 'form',
                title: 'Atendimento',
                border: false,
                frame: true,
                scope: this,
                height: 520,
                items: [
                    this.getItemsMainPanel(cfg)
                ]
            });
        return this._mainTab;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: false,

                items: [{
                    xtype: 'tabpanel',
                    activeTab: 0,
                    items: this.getTabPanelItems(cfg)
                }]
            });
        }

        return this._formPanel;
    },

    getTabPanelItems: function(cfg){
        return [
            this.getMainPanel(cfg),
            this.getAttachmentGrid(cfg)
        ];
    },

    finalize: function() {
        Ext._create('common.saci.attendance.FinalizeWindow', {
            action: 'create',
            modal: true,
            oId: this.attendance(),
            callback: {
                success: {
                    scope: this,
                    fn: function(instance) {
                        core.invokeCallback((this.callback || {}).success);
                        this.close();
                    }
                }
            }
        }).show();
    },

    forwardExternal: function() {
        Ext._create('common.saci.attendance.ForwardExternalWindow', {
            action: 'create',
            modal: true,
            oId: this.attendance(),
            callback: {
                success: {
                    scope: this,
                    fn: function(instance) {
                        core.invokeCallback((this.callback || {}).success);
                        this.close();
                    }
                }
            }
        }).show();
    },

    forward: function() {
        Ext._create('common.saci.attendance.ForwardWindow', {
            action: 'create',
            modal: true,
            oId: this.attendance(),
            callback: {
                success: {
                    scope: this,
                    fn: function(instance) {
                        core.invokeCallback((this.callback || {}).success);
                        this.close();
                    }
                }
            }
        }).show();
    },

    getFinalizeButton: function(cfg) {
        if(!this._finalizeButton)
            this._finalizeButton = Ext._create('Ext.Button', {
                text: 'Finalizar',
                scope: this,
                handler: this.finalize,
                disabled: true
            });

        return this._finalizeButton;
    },

    getForwardButton: function(cfg) {
        if(!this._forwardButton)
            this._forwardButton = Ext._create('Ext.Button', {
                text: 'Encaminhamento interno',
                scope: this,
                handler: this.forward,
                disabled: true
            });

        return this._forwardButton;
    },

    getForwardExternalButton: function(cfg) {
        if(!this._forwardExternalButton)
            this._forwardExternalButton = Ext._create('Ext.Button', {
                text: 'Encaminhamento externo',
                scope: this,
                handler: this.forwardExternal,
                disabled: true
            });

        return this._forwardExternalButton;
    },

    attendance: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._attendance = value;

            if(dispatch)
                this.observeAttendance();
        }

        return this._attendance;
    },

    observeAttendance: function() {
        var value = this.attendance();

        this.changeButtons(value);
        this.loadAttachment(value);
    },

    getItemsButton: function(cfg) {
        return [
            this.getFinalizeButton(cfg),
            this.getForwardExternalButton(cfg),
            this.getForwardButton(cfg)
        ];
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                this.getItemsButton(cfg),
                '->',
            ].concat(common.saci.attendance.Window.superclass.getButtons.call(this, cfg));

        return this._buttons;
    },

    changeButtons: function(value) {
        if(value){
            this.getFinalizeButton().enable();
            this.getForwardButton().enable();
            this.getForwardExternalButton().enable();
        } else {
            this.getFinalizeButton().disable();
            this.getForwardButton().disable();
            this.getForwardExternalButton().disable();
        }
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
                fieldLabel: 'Nível de acesso',
                emptyText: 'Deixe em branco para classificar como público',
                allowBlank: true,
                displayField: 'title',
                rest: 'common.document_access.controltype.byUser.Restful',
                anchor: '98%',
                submitValue: false,  // Não submeter.
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
                control_type: ((cfg || {}).values || {}).control_type || 0
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

    getControlContainer: function (cfg) {
        if (!this._controlContainer) {
            this._controlContainer = Ext._create('Ext.Container', {
                layout: 'hbox',
                items: [
                    {
                        xtype: 'container',
                        layout: 'form',
                        flex: 3.0,
                        items: this.getControlTypeField(cfg)
                    },
                    {
                        xtype: 'container',
                        layout: 'form',
                        flex: 1.0,
                        items: this.getAllowedListButton(cfg)
                    }
                ]
            });
        }

        return this._controlContainer;
    },

    showAllowedListWindow: function (cfg) {
        var control = ((cfg || {}).values || {}).control || 0;

        Ext._create('common.document_access.allowedlistitem.Modal', {
            control: control,
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
            var control = ((cfg || {}).values || {}).control || 0;

            this._allowedListButton = Ext._create('Ext.Button', {
                text: 'Credenciais de acesso',
                width: 150,
                iconCls: 'icon-document_access icon-document_access-allowedlist',
                scope: this,
                disabled: (control ? false : true),
                handler: function() {
                    this.showAllowedListWindow(cfg);
                }
            });
        }

        return this._allowedListButton;
    },

    accessControl: function(values) {
        var rest = Ext._create('common.saci.attendance.Restful');
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Classificando informação...'});

        mask.show();
        rest.accessControl(
            this.oId,
            values,
            {
                scope: this,
                fn: function(result) {
                    if (result.success) {
                        this.getAllowedListButton().enable();

                        if (this.ownerGrid) {
                            this.ownerGrid.getStore().reload();
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
                }
            },
            {
                scope: this,
                fn: function(message) {
                    this.getControlTypeField().undoChange();

                    Ext.Msg.show({
                        title: 'Classificando informação',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function() {
                    mask.hide();
                }
            }
        );
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
                    control_type: controlType,
                    legal_prerogative: legalPrerogative,
                    justification: justification,
                });
            },
            failure: function (error) {
                this.getControlTypeField().undoChange();
            }
        }).show();
    },

    saveAndContinueCallback: function (instance) {
        this.action = 'update';
        this.oId = instance.pk;
        this.attendance(instance.pk);

        if (this.hasControlTypeChanged()) {
            this.showJustificationWindow();
        }
    },

    postConstructor: function (cfg) {
        if (cfg.oId || this.oId) {
            this.attendance(cfg.oId || this.oId);
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                buttonAlign: 'left',
                disableSaveAndNew: true,
                saveAndContinue: {
                    scope: this,
                    fn: this.saveAndContinueCallback
                },
                border: false
            }
        );

        common.saci.attendance.Window.superclass.constructor.call(this, cfg);
        this.postConstructor(cfg);
    }
});
