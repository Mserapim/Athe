Ext._define('common.document_access.JustificationWindow', {
    extend: 'Ext.Window',

    getLegalPrerogativeField: function (cfg) {
        if (!this._legalPrerogativeField) {
            this._legalPrerogativeField = Ext._create('core.fields.ComboField', {
                name: 'legal_prerogative',
                fieldLabel: 'Hipótese legal',
                allowBlank: false,
                displayField: 'title',
                rest: 'common.document_access.legalprerogative.Restful',
                anchor: '99%',
                preFilter: [
                    {property: 'control_type', value: cfg.controlType, stage: 1001},
                    {property: 'enabled', value: true, stage: 1002},
                ],
                listeners: {
                    scope: this,
                    select: function (combo, record, index) {
                        this.getJustificationField().setValue(
                            combo.getStore().getAt(index).get('description')
                        );
                    }
                }
            });
        }

        return this._legalPrerogativeField;
    },

    getJustificationField: function (cfg) {
        if (!this._justificationField) {
            cfg.configCKEditor = cfg.configCKEditor || {};

            Ext.applyIf(cfg.configCKEditor, {
                allowBlank: false,
                height: 300,
                editorConfig: {toolbarStartupExpanded: true},
            });

            Ext.apply(cfg.configCKEditor, {
                hideLabel: true,
            });

            this._justificationField = Ext._create('toolkit.fields.CKEditor', cfg.configCKEditor);
        }

        return this._justificationField;
    },

    getCancelButton: function (cfg) {
        if (!this._cancelButton) {
            var self = this;

            this._cancelButton = Ext._create('Ext.Button', {
                text: 'Cancelar',
                scope: this,
                handler: function () {
                    function cancel() {
                        if (Ext.isFunction(cfg.failure)) {
                            cfg.failure.call(cfg.scope || self, 'canceled');
                        }

                        self.close();
                    }

                    if (cfg.showDialogWhenCanceling) {
                        Ext.Msg.show({
                            title: 'Classificando informação',
                            msg: 'Esta ação cancelará a classificação da informação do documento. Prosseguir com o cancelamento?',
                            icon: Ext.Msg.QUESTION,
                            buttons: Ext.Msg.YESNO,
                            scope: self,
                            fn: function(btn) { if (btn == 'yes') cancel(); }
                        });
                    } else {
                        cancel();
                    }
                }
            });
        }

        return this._cancelButton;
    },

    getSaveButton: function (cfg) {
        if (!this._saveButton) {
            this._saveButton = Ext._create('Ext.Button', {
                text: 'Salvar',
                scope: this,
                handler: function () {
                    this.validateFields();

                    var legalPrerogative = this.getLegalPrerogativeField().getValue();
                    var justification = this.getJustificationField().getValue();

                    cfg.handler.call(cfg.scope || this, justification, legalPrerogative);

                    this.close();
                }
            });
        }

        return this._saveButton;
    },

    validateFields: function () {
        function showError(msg) {
            Ext.Msg.show({
                title: 'Validando',
                msg: msg,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                minWidth: 400,
            });
            throw msg;
        }

        if (!this.getLegalPrerogativeField().isValid(true)) {
            showError('Por favor, preencha o campo Hipótese Legal.');
        }

        if (!this.getJustificationField().isValid(true)) {
            showError('Por favor, preencha o campo Justificativa.');
        }
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                height: 475,
                labelWidth: 90,
                items: [
                    this.getLegalPrerogativeField(cfg),
                    {
                        xtype: 'panel',
                        title: cfg.ckeditorPanelTitle,
                        items: this.getJustificationField(cfg),
                    }
                ]
            });
        }

        return this._formPanel;
    },

    _raiseError: function (error, cfg) {
        Ext.Msg.show({
            title: 'Erro de implementação',
            msg: error,
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK
        });

        if (Ext.isFunction(cfg.failure)) {
            cfg.failure.call(cfg.scope || this, error);
        }

        throw new TypeError('Erro de implementação: ' + error);
    },

    _validate_config: function (cfg) {
        if (!Ext.isFunction(cfg.handler)) {
            this._raiseError('Forneça uma config handler válida.', cfg);
        }

        if (!Ext.isNumber(cfg.controlType)) {
            this._raiseError('Forneça uma config controlType válida.', cfg);
        }
    },

    /**
     * Custom configs:
     * 
     * @param {Number} cfg.controlType Required. Qualquer id de uma instância de ControlType.
     * @param {Function} cfg.handler Required. Função de callback chamada quando o botão Salvar é clicado.
     * @param {Function} cfg.failure Optional. Função de callback que é chamada quando o botão Cancelar é clicado, ou quando ocorre um erro de implementação.
     * @param {Object} cfg.scope Optional. Objeto "this" para callbacks.
     * @param {Object} cfg.configCKEditor Optional. Configs para campos que utilizam CKEditor.
     * @param {String} cfg.ckeditorPanelTitle Optional. Título para o painel que contém o CKEditor.
     * @param {boolean} cfg.showDialogWhenCanceling Optional. Mostrar caixa de diálogo de confirmação quando o botão Cancelar é clicado. O padrão é não mostrar.
     */
    constructor: function (cfg) {
        cfg = cfg || {};

        this._validate_config(cfg);

        Ext.applyIf(cfg, {
            ckeditorPanelTitle: ((cfg.configCKEditor || {}).fieldLabel || 'Justificativa'),
            title: 'Justificativa',
            modal: true,
            resizable: false,
            width: 900,
            height: 'auto',
            autoHeight: true,
            border: false,
            closable: false,
        });

        Ext.apply(cfg, {
            layout: 'fit',
            items: this.getFormPanel(cfg),
            buttons: [
                this.getSaveButton(cfg),
                this.getCancelButton(cfg),
            ],
        });

        common.document_access.JustificationWindow.superclass.constructor.call(this, cfg);
    }
});
