Ext._define('edocs.protocolo.requestform.electorallicense.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestFormElectoralLicense',

    rest: 'edocs.protocolo.requestform.electorallicense.Restful',

    width: 900,

    getDescriptionField: function (cfg) {
        if (!this._descriptionField) {
            this._descriptionField = Ext._create('Ext.Panel', {
                title: 'Descrição (informe uma ou mais datas de licença)',
                items: [{
                    xtype: 'ckeditor',
                    name: 'description',
                    height: 150,
                    allowBlank: false,
                }]
            });
        }

        return this._descriptionField;
    },

    getMainPanel: function (cfg) {
        if (!this._mainPanel) {
            this._mainPanel = Ext._create('Ext.Panel', {
                frame: false,
                border: false,
                layout: 'form',
                items: [
                    {
                        xtype: 'panel',
                        layout: 'form',
                        frame: true,
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
                                value: 'Requerimento Licença Eleitoral',
                                readOnly: true,
                            }),
                            this.getControlContainer(cfg),
                            this.getContactNumberField(cfg),
                        ]
                    },
                    this.getDescriptionField(cfg),
                ]
            });
        }

        return this._mainPanel;
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
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
    title: 'Requerimento Licença Eleitoral',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.electorallicense.Window',
    specialType: 'electorallicense',
    group: 'Licenças e afastamentos'
});
