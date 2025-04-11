Ext._define('common.document_access.legalprerogative.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.document_access.legalprerogative.Restful',

    width: 900,

    getControlTypeField: function (cfg) {
        if (!this._controlTypeField) {
            this._controlTypeField = Ext._create('core.fields.AutocompleteField', {
                name: 'control_type',
                fieldLabel: 'Nível de acesso',
                rest: "common.document_access.controltype.Restful",
                allowBlank: false,
                readOnly: true,
                hidden: true,
            });
        }

        return this._controlTypeField;
    },

    getFormPanel: function(cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 50,
                items: [
                    {
                        xtype: 'container',
                        layout: 'hbox',
                        items: [
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 1.0,
                                labelWidth: 50,
                                items: [
                                    {
                                        name: "title",
                                        fieldLabel: "Título",
                                        xtype: "textfield",
                                        allowBlank: false,
                                        maxLength: 150,
                                        anchor: '95%',
                                    }
                                ]
                            },
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 0.1,
                                items: [
                                    {
                                        name: "enabled",
                                        boxLabel: "Habilitado",
                                        xtype: "checkbox",
                                        allowBlank: true,
                                        hideLabel: true,
                                    }
                                ]
                            }
                        ]
                    },
                    this.getControlTypeField(cfg),
                    {
                        xtype: 'panel',
                        title: 'Descrição',
                        style: {marginTop: '5px'},
                        items: [
                            {
                                name: "description",
                                xtype: "ckeditor",
                                allowBlank: false,
                                height: 380
                            },
                        ],
                    },
                ]
            });
        }

        return this._formPanel;
    },

    afterSaveAndNew: function () {
        var self = this;

        setTimeout(function() {
            self.getControlTypeField().setValue(self.params.control_type);
        }, 500);
    },

    getButtons: function(cfg) {
        if (!this._buttons) {
            this._buttons = [];

            if (cfg.action == 'create' && !cfg.disableSaveAndNew) {
                this._buttons.push({
                    text: 'Salvar e novo',
                    scope: this,
                    handler: function() {
                        this.save(false);
                        this.afterSaveAndNew();
                    }
                });
            }

            if (!cfg.disableSave) {
                this._buttons.push({
                    text: 'Salvar',
                    scope: this,
                    handler: function() { this.save(true); }
                });
            }

            this._buttons.push({
                text: 'Fechar',
                scope: this,
                handler: this.destroy
            });
        }

        return this._buttons;
    },
});
