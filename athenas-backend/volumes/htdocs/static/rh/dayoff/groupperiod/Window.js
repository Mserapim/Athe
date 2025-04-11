Ext._define("rh.dayoff.groupperiod.Window", {
    extend: "core.RestfulWindow",

    rest: "rh.dayoff.groupperiod.Restful",

    width: 600,

    height: 620,

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create("Ext.form.FormPanel", {
                border: false,
                items: this.getTabPanel(cfg),
                submit_all_checks: true,
            });

        return this._formPanel;
    },

    getAttachmentField: function () {
        if (!this._attachmentField)
            this._attachmentField = Ext._create("Ext.Panel", {
                border: false,
                frame: false,
                layout: "form",
                items: [this.getAttachmentButton(), this.getAttachment()],
            });

        return this._attachmentField;
    },

    getAttachment: function (v) {
        if (!this._attachment) {
            this._attachment = Ext._create("Ext.form.TextField", {
                fieldLabel: "Anexo",
                name: "attachment",
                allowBlank: true,
                hidden: true,
            });
        }
        return this._attachment;
    },

    getAttachmentButton: function () {
        if (!this._attachmentButton) {
            this._attachmentButton = Ext._create("Ext.Button", {
                text: "Visualizar Anexo",
                fieldLabel: "Anexo",
                anchor: "50%",
                scope: this,
                handler: this.getAttachmentWindow,
            });
        }
        return this._attachmentButton;
    },

    getAttachmentWindow: function () {
        attachment_value = this.getFormPanel().getForm().findField("attachment").getValue();
        if (attachment_value === undefined || attachment_value === "") {
            action = "create";
            oId_value = null;
        } else {
            action = "update";
            oId_value = attachment_value;
        }
        Ext._create("rh.dayoff.attachment.Window", {
            title: "Anexo",
            oId: oId_value,
            action: action,
            values: "remote",
            callback: {
                success: {
                    scope: this,
                    fn: function (instance) {
                        this.getFormPanel().getForm().findField("attachment").setValue(instance.pk);
                    },
                },
            },
        }).show();
    },

    getTabPanel: function (cfg) {
        if (!this._tabPanel)
            this._tabPanel = Ext._create("Ext.TabPanel", {
                height: 630,
                border: false,
                activeTab: 0,
                deferredRender: false,
                items: [this.getManagementPanel(cfg), this.getEmployeePanel(cfg)],
            });

        return this._tabPanel;
    },

    getEmployeePanel: function (cfg) {
        if (!this._employeePanel)
            this._employeePanel = Ext._create("core.fields.RelatedRestfulField", {
                title: "Servidores excluídos da geração de usufrutos",
                name: "employee_not_create_usufrutcs",
                width: 590,
                height: 550,
                rest: this.rest,
                disabled: false,
                sourceRest: "rh.employee.Restful",
                oId: cfg.oId,
                preFilter: [
                    {
                        property: "ativo",
                        value: true,
                    },
                ],
            });

        return this._employeePanel;
    },

    getManagementPanel: function (cfg) {
        if (!this._managementPanel)
            this._managementPanel = Ext._create("Ext.Panel", {
                frame: true,
                border: false,
                title: "Gerenciamento",
                labelWidth: 200,
                defaults: {
                    width: 360,
                },
                layout: "form",
                items: [
                    {
                        name: 'title',
                        fieldLabel: 'Identifica\u00e7\u00e3o *',
                        xtype: 'textfield',
                        allowBlank: false,
                        maxLength: 100,
                    },
                    {
                        name: 'configuration',
                        fieldLabel: 'Configura\u00e7\u00e3o *',
                        xtype: 'rest-autocompletefield',
                        allowBlank: false,
                        rest: "rh.dayoff.configuration.Restful",
                    },
                    {
                        name: 'year_reference',
                        fieldLabel: 'Ano de Referência *',
                        xtype: 'numberfield',
                        allowBlank: true,
                        allowDecimals: false,
                    },
                    {
                        name: 'period',
                        fieldLabel: 'Per\u00edodo *',
                        xtype: 'numberfield',
                        allowBlank: false,
                        allowDecimals: false,
                        value: 1,
                    },
                    {
                        name: 'start_date_book',
                        fieldLabel: 'In\u00edcio de marca\u00e7\u00e3o *',
                        xtype: 'datefield',
                        allowBlank: false,
                    },
                    {
                        name: "end_date_book",
                        fieldLabel: "Final de marca\u00e7\u00e3o",
                        xtype: "datefield",
                        allowBlank: true,
                    },
                    {
                        name: "homologation_date",
                        fieldLabel: "Data de Homologa\u00e7\u00e3o",
                        xtype: "datefield",
                        allowBlank: true,
                    },
                    {
                        name: "publication_date",
                        fieldLabel: "Data de Publica\u00e7\u00e3o",
                        xtype: "datefield",
                        allowBlank: true,
                    },
                    {
                        name: 'start_date_fruition',
                        fieldLabel: 'Início da fruição(período para fruição) *',
                        xtype: 'datefield',
                        allowBlank: false,
                    },
                    {
                        name: "end_date_fruition",
                        fieldLabel: "Fim da fruição(período para fruição)",
                        xtype: "datefield",
                        allowBlank: true,
                    },
                    {
                        name: "start_date_automatic_usufruct",
                        fieldLabel: "Data de Inicio de Usufruto Automático",
                        xtype: "datefield",
                        allowBlank: true,
                    },
                    {
                        name: "end_date_automatic_usufruct",
                        fieldLabel: "Data de Fim de Usufruto Automático",
                        xtype: "datefield",
                        allowBlank: true,
                    },
                    {
                        name: "redo_automatic_book",
                        fieldLabel: "Refazer a marcação automática de usufruto",
                        xtype: "checkbox",
                        allowBlank: false,
                    },
                    {
                        name: "start_date_acquisition",
                        fieldLabel: "Início aquisição(Quando preenchido)",
                        xtype: "datefield",
                        allowBlank: true,
                    },
                    {
                        name: "end_date_acquisition",
                        fieldLabel: "Fim aquisição(Quando preenchido)",
                        xtype: "datefield",
                        allowBlank: true,
                    },
                    {
                        name: "blocked",
                        fieldLabel: "Bloqueado",
                        xtype: "checkbox",
                        allowBlank: false,
                    },
                    this.getAttachmentField(),
                ],
            });

        return this._managementPanel;
    },
});

