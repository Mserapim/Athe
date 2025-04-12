Ext._define('edocs.protocolo.requestform.removenotificationresistance.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RFRemoveNotificationResistance',

    rest: 'edocs.protocolo.requestform.removenotificationresistance.Restful',

    width: 900,
    height: 500,

    getCancellationVacanciesField: function (cfg) {
        if (!this._cancellationVacanciesField) {
            this._cancellationVacanciesField = Ext._create('Ext.form.FieldSet', {
                title: "Vagas de desistência",
                layout: 'anchor',
                items: [
                    {
                        xtype: 'ckeditor',
                        name: 'cancellation_vacancies',
                        height: 100,
                        toolbarGroups: [
                            { name: 'styles', itens: ['Format'] },
                            { name: 'clipboard' },
                            { name: 'editing' },
                            { name: 'basicstyles', groups: ['basicstyles', 'cleanup'] },
                            {
                                name: 'paragraph',
                                groups: ['list', 'indent', 'blocks', 'align', 'bidi'],
                            }
                        ],
                    }
                ]
            });
        }

        return this._cancellationVacanciesField;
    },

    getResistanceDeclaration: function (cfg) {
        if (!this._resistanceDeclarationField) {
            this._resistanceDeclarationField = Ext._create('Ext.form.FieldSet', {
                title: "Declaração de desistência",
                layout: 'anchor',
                items: [
                    {
                        xtype: 'ckeditor',
                        name: 'resistance_declaration',
                        height: 100,
                        toolbarGroups: [
                            { name: 'styles', itens: ['Format'] },
                            { name: 'clipboard' },
                            { name: 'editing' },
                            { name: 'basicstyles', groups: ['basicstyles', 'cleanup'] },
                            {
                                name: 'paragraph',
                                groups: ['list', 'indent', 'blocks', 'align', 'bidi'],
                            }
                        ],
                    }
                ]
            });
        }

        return this._resistanceDeclarationField;
    },

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
                                    style: 'margin-left: 15px',
                                    layout: 'form',
                                    flex: 1.25,
                                    labelWidth: 30,
                                    items: this.getDocumentTypeField('REQUERIMENTO')  // mixin
                                },
                            ]
                        },
                        this.getSubjectField(cfg, {
                            value: 'Desistência Edital de Remoção n. 02/2022',
                            readOnly: true,
                        }),
                        this.getControlContainer(cfg),
                    ],
                },
                this.getCancellationVacanciesField(cfg),
                // this.getResistanceDeclaration(cfg)
            ],
        });

        return this._mainPanel;
    },

    getMainInfoPanel: function (cfg) {
        if (this._mainFormPanel) {
            return this._mainFormPanel;
        }

        this._mainFormPanel = Ext._create('Ext.Panel', {
            title: 'Informações',
            frame: false,
            autoHeight: true,
            items: [
                this.getMainPanel(cfg),
            ],
        });

        return this._mainFormPanel;
    },

    getTabPanel: function (cfg) {
        if (!this._tabPanel) {
            this._tabPanel = Ext._create('Ext.TabPanel', {
                activeTab: 0,
                border: false,
                deferredRender: false,
                items: [
                    this.getMainInfoPanel(cfg),
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
    title: 'Desistência Edital de Remoção',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.removenotificationresistance.Window',
    specialType: 'removenotificationresistance'
});
