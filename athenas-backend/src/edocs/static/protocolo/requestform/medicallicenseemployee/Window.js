Ext._define('edocs.protocolo.requestform.medicallicenseemployee.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RFMedicalLicenseEmployee',

    rest: 'edocs.protocolo.requestform.medicallicenseemployee.Restful',

    width: 900,

    height: 450,

    getMainPanel: function (cfg) {
        if (this._mainPanel) {
            return this._mainPanel;
        }

        this._mainPanel = Ext._create('Ext.Panel', {
            frame: true,
            layout: 'form',
            labelWidth: 90,
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
                            value: 'Requerimento Licença Junta Médica do Servidor',
                            readOnly: true,
                        }),
                        this.getControlContainer(cfg),
                    ]
                },
            ]
        });

        return this._mainPanel;
    },

    getInformativePanel: function (cfg) {
        if (this._informativePanel) {
            return this._informativePanel;
        }

        this._informativePanel = Ext._create('Ext.Panel', {
            frame: true,
            layout: 'form',
            labelWidth: 90,
            xtype: 'fieldset',
            items: [
                {
                    xtype: 'displayfield',
                    layout: 'fit',
                    html: '<div style="padding:10px;">' +
                        '<b>' +
                            'Licença para tratamento de saúde' +
                        '</b>' +
                        '<ul>' +
                            '<li style="list-style: decimal inside; margin: 5px 0;">Atestado Médico;</li>' +
                            '<li style="list-style: decimal inside; margin: 5px 0;">Resultado do Exames Laboratoriais realizados, quando for o caso;</li>' +
                            '<li style="list-style: decimal inside; margin: 5px 0;">Declaração Hospitalar com data de internação e alta, quando for o caso;</li>' +
                            '<li style="list-style: decimal inside; margin: 5px 0;">Cópia do último contracheque.</li>' +
                        '</ul>' +
                        '<p style="padding-bottom:10px;"></p>' +
                        '<b>' +
                            'Licença por motivo de doença em pessoa da família' +
                        '</b>' +
                        '<ul>' +
                            '<li style="list-style: decimal inside; margin: 5px 0;">Atestado Médico;</li>' +
                            '<li style="list-style: decimal inside; margin: 5px 0;">Resultado do Exames Laboratoriais realizados, quando for o caso;</li>' +
                            '<li style="list-style: decimal inside; margin: 5px 0;">Declaração Hospitalar com data de internação e alta, quando for o caso;</li>' +
                            '<li style="list-style: decimal inside; margin: 5px 0;">Cópia do último contracheque;</li>' +
                            '<li style="list-style: decimal inside; margin: 5px 0;">Declaração de Acompanhante;</li>' +
                            '<li style="list-style: decimal inside; margin: 5px 0;">Comprovante de Parentesco conforme o vínculo familiar existente.</li>' +
                        '</ul>' +
                        '<p style="padding-bottom:10px;"></p>' +
                        '<b>' +
                            'Licença maternidade ou adoção' +
                        '</b>' +
                        '<ul>' +
                            '<li style="list-style: decimal inside; margin: 5px 0;">Atestado Médico;</li>' +
                            '<li style="list-style: decimal inside; margin: 5px 0;">Certidão de Nascimento da Criança;</li>' +
                            '<li style="list-style: decimal inside; margin: 5px 0;">Cópia do último contracheque.</li>' +
                        '</ul>' +
                    '</div>',
                    collapsible: false,
                },
            ],
        });

        return this._informativePanel;
    },

    getMainInfoPanel: function (cfg) {
        if (this._mainFormPanel) {
            return this._mainFormPanel;
        }

        this._mainFormPanel = Ext._create('Ext.Panel', {
            title: 'Informações',
            frame: false,
            items: [
                this.getMainPanel(cfg),
                {
                    layout: 'vbox',
                    border: false,
                    height: 250,
                    padding: '10px 0 0 0',
                    items: this.getAttachmentPanel(cfg)
                }
            ],
        });

        return this._mainFormPanel;
    },

    getMainInformativePanel: function (cfg) {
        if (this._informativeFormPanel) {
            return this._informativeFormPanel;
        }

        this._informativeFormPanel = Ext._create('Ext.Panel', {
            title: 'Instruções',
            frame: false,
            items: [
                this.getInformativePanel(cfg),
            ],
        });

        return this._informativeFormPanel;
    },

    getTabPanel: function (cfg) {
        if (!this._tabPanel) {
            this._tabPanel = Ext._create('Ext.TabPanel', {
                activeTab: 0,
                border: false,
                items: [
                    this.getMainInfoPanel(cfg),
                    this.getMainInformativePanel(cfg)
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
    title: 'Requerimento Licença Junta Médica do Servidor',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.medicallicenseemployee.Window',
    specialType: 'medicallicenseemployee',
    group: 'Licenças e afastamentos'
});
