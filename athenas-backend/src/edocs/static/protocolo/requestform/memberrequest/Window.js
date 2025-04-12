Ext._define('edocs.protocolo.requestform.memberrequest.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestFormMember',

    rest: 'edocs.protocolo.requestform.memberrequest.Restful',

    width: 900,

    getRequestTypeField: function (cfg) {
        if (!this._requestTypeField) {
            this._requestTypeField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Requerimento',
                editable: false,
                hiddenName: 'request_type',
                anchor: '99%',
                choiceId: 'requestform.MEMBER_REQUEST_TYPE',
                allowBlank: false
            });
        }

        return this._requestTypeField;
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
                        items: [
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 2.75,
                                items: this.getHomeCourtField(cfg)
                            },
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 1.25,
                                labelWidth: 50,
                                items: this.getDocumentTypeField('REQUERIMENTO')  // mixin
                            }
                        ]
                    },
                    this.getSubjectField(cfg, {
                        value: 'Requerimento Promotor e Procurador de Justiça',
                        readOnly: true,
                    }),
                    this.getControlContainer(cfg),
                    this.getRequestTypeField(cfg)
                ]
            });
        }

        return this._mainPanel;
    },

    getInformationPanel: function (cfg) {
        if (!this._informationPanel) {
            this._informationPanel = Ext._create('Ext.Panel', {
                title: 'Informações',
                frame: false,
                items: [
                    this.getMainPanel(cfg),
                    {
                        layout: 'vbox',
                        border: false,
                        height: 250,
                        items: this.getAttachmentPanel(cfg),
                    },
                ]
            });
        }

        return this._informationPanel;
    },

    getContentPanel: function (cfg) {
        if (!this._contentPanel) {
            this._contentPanel = Ext._create('Ext.Panel', {
                title: 'Descrição do pedido',
                frame: false,
                items: [{
                    xtype: 'ckeditor',
                    name: 'content',
                    height: 289,
                }]
            });
        }

        return this._contentPanel;
    },

    getTabPanel: function (cfg) {
        if (!this._tabPanel) {
            this._tabPanel = Ext._create('Ext.TabPanel', {
                activeTab: 0,
                border: false,
                deferredRender: false,
                items: [
                    this.getInformationPanel(cfg),
                    this.getContentPanel(cfg)
                ]
            });
        }

        return this._tabPanel;
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: this.getTabPanel(cfg)
            });
        }

        return this._formPanel;
    }
});

edocs.protocolo.box.MainGrid.registerSpecialType({
    title: 'Requerimento Promotor e Procurador de Justiça',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.memberrequest.Window',
    specialType: 'memberrequest',
    group: 'Requerimento gerais para integrantes'
});
