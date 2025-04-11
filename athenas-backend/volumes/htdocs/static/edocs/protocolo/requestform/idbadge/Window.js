Ext._define('edocs.protocolo.requestform.idbadge.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestFormIdBadge',

    rest: 'edocs.protocolo.requestform.idbadge.Restful',

    width: 900,

    getIsReissueField: function (cfg) {
        if (!this._isReissueField) {
            this._isReissueField = Ext._create('Ext.form.Checkbox', {
                boxLabel: '2ª Via',
                name: 'is_reissue',
                value: 'off',
            });
        }

        return this._isReissueField;
    },

    getReissueReasonField: function (cfg) {
        if (!this._reissueReasonField) {
            this._reissueReasonField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Motivo da 2ª via',
                editable: false,
                hiddenName: 'reissue_reason',
                width: 200,
                choiceId: 'requestform.FUNCTIONALIDENTITY_REISSUE_REASON'
            });
        }

        return this._reissueReasonField;
    },

    getDisplayNameField: function (cfg) {
        if (!this._displayNameField) {
            this._displayNameField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Nome no crachá',
                name: 'display_name',
                anchor: '99%'
            });
        }

        return this._displayNameField;
    },

    getMainPanel: function (cfg) {
        if (!this._mainPanel) {
            this._mainPanel = Ext._create('Ext.Panel', {
                frame: true,
                layout: 'form',
                items: [
                    {
                        xtype: 'fieldset',
                        items: [
                            this.getCodeField(cfg),
                            {
                                xtype: 'container',
                                layout: 'hbox',
                                items: [
                                    {
                                        xtype: 'container',
                                        layout: 'form',
                                        flex: 2.75,
                                        labelWidth: 60,
                                        items: this.getHomeCourtField(cfg)
                                    },
                                    {
                                        xtype: 'container',
                                        layout: 'form',
                                        flex: 1.25,
                                        labelWidth: 50,
                                        items: this.getDocumentTypeField('REQUERIMENTO'),  // mixin
                                    }
                                ]
                            },
                            this.getSubjectField(cfg, {
                                value: 'Requerimento para Confecção de Crachá',
                                readOnly: true,
                            }),
                            this.getControlContainer(cfg),
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        layout: 'form',
                        items: [
                            {
                                xtype: 'container',
                                layout: 'hbox',
                                items: [
                                    {
                                        xtype: 'container',
                                        layout: 'form',
                                        flex: 1.0,
                                        labelWidth: 1,
                                        items: this.getIsReissueField(cfg)
                                    },
                                    {
                                        xtype: 'container',
                                        layout: 'form',
                                        flex: 6.0,
                                        labelWidth: 100,
                                        items: this.getReissueReasonField(cfg)
                                    }
                                ]
                            },
                            {
                                xtype: 'container',
                                layout: 'form',
                                labelWidth: 100,
                                items: this.getDisplayNameField(cfg)
                            }
                        ]
                    }
                ]
            });
        }

        return this._mainPanel;
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                height: 'auto',
                autoHeight: true,
                items: [
                    this.getMainPanel(cfg),
                    {
                        layout: 'vbox',
                        border: false,
                        height: 200,
                        items: this.getAttachmentPanel(cfg)
                    }
                ]
            });
        }

        return this._formPanel;
    }
});

edocs.protocolo.box.MainGrid.registerSpecialType({
    title: 'Requerimento Confecção de Crachá',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.idbadge.Window',
    specialType: 'idbadge',
    group: 'Requerimento gerais para integrantes'
});
