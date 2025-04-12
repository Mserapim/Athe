Ext._define('edocs.protocolo.requestform.homeoffice.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RFHomeOfficeForEmployee',

    rest: 'edocs.protocolo.requestform.homeoffice.Restful',

    width: 900,
    height: 825,

    getRequestTypeField: function (cfg) {
        return this.getChoiceFieldSet({
            title: 'CONDIÇÃO DO SERVIDOR (art. 8º, V, do Ato PGJ n. 021/2022)',
            name: 'request_type',
            value: (cfg.values || {}).request_type,
            choiceId: 'requestform.HOME_OFFICE_FOR_EMPLOYEE_REQTYPE',
        });
    },

    getJustificationFieldSet: function (cfg) {
        if (this._justificationFieldSet)
            return this._justificationFieldSet;

        this._justificationFieldSet = Ext._create('Ext.form.FieldSet', {
            title: 'JUSTIFICATIVA',
            layout: 'anchor',
            items: [
                {
                    xtype: 'ckeditor',
                    name: 'justification',
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
                    ]
                }
            ]
        });
        return this._justificationFieldSet;
    },

    getActivitiesAndGoalsFieldSet: function (cfg) {
        if (this._activitiesFieldSet)
            return this._activitiesFieldSet;

        this._activitiesFieldSet = Ext._create('Ext.form.FieldSet', {
            title: 'ATIVIDADES E METAS',
            layout: 'anchor',
            items: [
                {
                    xtype: 'ckeditor',
                    name: 'activities_goals',
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
                    ]
                }
            ]
        });
        return this._activitiesFieldSet;
    },

    getscheduleFieldSet: function (cfg) {
        if (this._scheduleFieldSet)
            return this._scheduleFieldSet;

        this._scheduleFieldSet = Ext._create('Ext.form.FieldSet', {
            title: 'CRONOGRAMA DE REUNIÕES COM CHEFIA',
            layout: 'anchor',
            items: [
                {
                    xtype: 'ckeditor',
                    name: 'schedule',
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
                    ]
                }
            ]
        });
        return this._scheduleFieldSet;
    },

    getWorkPlanPanel: function (cfg) {
        if (!this._contentPanel) {
            this._contentPanel = Ext._create('Ext.Panel', {
                title: 'Plano de Trabalho',
                frame: false,
                padding: 10,
                items: [
                  this.getActivitiesAndGoalsFieldSet(cfg),
                  this.getscheduleFieldSet(cfg)
                ]
            });
        }

        return this._contentPanel;
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
                            value: 'Requerimento de Teletrabalho',
                            readOnly: true,
                        }),
                        this.getControlContainer(cfg),
                    ],
                },
                this.getRequestTypeField(cfg),
                this.getJustificationFieldSet(cfg),
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
                {
                    layout: 'vbox',
                    border: false,
                    height: 170,
                    padding: '10px 0 0 0',
                    items: this.getAttachmentPanel(cfg)
                },
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
                    this.getWorkPlanPanel(cfg)
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
    title: 'Requerimento de Teletrabalho',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.homeoffice.Window',
    specialType: 'homeofficeforemployee',
    group: 'Teletrabalho'
    // specialType: 'healthcareallowanceforactiveemployee'
});
