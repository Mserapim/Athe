Ext._define('edocs.protocolo.requestform.removenotificationapplication.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RFRemoveNotificationApplication',

    rest: 'edocs.protocolo.requestform.removenotificationapplication.Restful',

    width: 900,
    height: 600,

    getPositionStartConcursoField: function (cfg) {
        if (!this._positionStartConcursoField) {
            this._positionStartConcursoField = Ext._create('Ext.form.TextField', {
                fieldLabel: "Posição no concurso de ingresso",
                name: "position_start_concurso",
                anchor: '99%',
            });
        }

        return this._positionStartConcursoField;
    },

    getOptionsInterestField: function (cfg) {
        if (!this._optionInterestField) {
            this._optionInterestField = Ext._create('Ext.form.FieldSet', {
                title: 'VAGAS DE INTERESSE – INDICAR POR ORDEM DE PREFERÊNCIA',
                layout: 'anchor',
                items: [
                    {
                        xtype: 'ckeditor',
                        name: 'option_interest',
                        height: 200,
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
                        value: '<p><br> 1ª opção - <br> 2ª opção - <br> 3ª opção - <br> 4ª opção - <br> 5ª opção - <br> 6ª opção - <br> </p>'
                    }
                ]
            });
        }

        return this._optionInterestField;
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
                            value: 'Inscrição Edital de Remoção n. 02/2022',
                            readOnly: true,
                        }),
                        this.getControlContainer(cfg),
                    ],
                },
                {
                    xtype: 'fieldset',
                    layout: 'hbox',
                    title: '',
                    items: [
                        {
                            xtype: 'container',
                            layout: 'form',
                            flex: 0.5,
                            labelWidth: 180,
                            items: this.getPositionStartConcursoField(cfg)
                        }
                    ]
                },
                this.getOptionsInterestField(cfg)
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
    title: 'Inscrição Edital de Remoção',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.removenotificationapplication.Window',
    specialType: 'removenotificationapplication'
});
