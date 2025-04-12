Ext._define('common.document_access.control.changes.BaseJustification', {
    extend: 'Ext.Window',

    getJustificationField: function() {
        if (!this._justificationField) {
            this._justificationField = Ext._create('toolkit.fields.CKEditor', {
                name: 'justification',
                allowBlank: false,
                hideLabel: true,
                height: 340,
                editorConfig: {toolbarStartupExpanded: true},
            });
        }

        return this._justificationField;
    },

    getFormFields: function() {
        return [{
            xtype: 'panel',
            title: 'Justificativa',
            layout: 'form',
            items: this.getJustificationField()
        }];
    },

    getFormPanel: function() {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                labelAlign: 'left',
                labelWidth: 110,
                items: this.getFormFields()
            });
        }

        return this._formPanel;
    },

    prepareValues: function() {
        return Ext.applyIf(
            {
                pk_set: this.selections.map(function(row) { return row.get('pk');}),
                action: this.action,
            },
            this.getFormPanel().getForm().getValues()
        );
    },

    commitAction: function() {
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Processando...'});
        mask.show();

        this.controlGrid.factoryRestful().changeControl(
            this.prepareValues(),
            {
                scope: this,
                fn: function(obj) {
                    Ext.Msg.show({
                        title: this.title,
                        icon: obj.success ? Ext.Msg.INFO : Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: obj.message,
                        minWidth: 350
                    });
                    if (obj.success) {
                        this.destroy();
                        this.controlGrid.getStore().reload();
                    }
                }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: this.title,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: message,
                        minWidth: 350
                    });
                }
            },
            {
                scope: this,
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    validateFields: function () {
        var exception = {title: 'Erro de validação'};

        if (this.getFormPanel().getForm().getValues().justification === '') {
            exception.message = 'Por favor, preencha corretamente a Justificativa.';
            throw exception;
        }
    },

    toAsk: function() {
        try {
            this.validateFields();
            Ext.Msg.show({
                title: 'Confirmação',
                msg: 'Tem certeza que deseja enviar essa justificativa?',
                buttons: Ext.Msg.YESNO,
                icon: Ext.Msg.QUESTION,
                width: 300,
                scope: this,
                fn: function(b) {
                    if (b == 'no')
                        return;

                    this.commitAction();
                }
            });
        } catch (e) {
            Ext.Msg.show({
                title: 'Erro de validação',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: e.message
            });
        }
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.apply(cfg, {
            modal: true,
            autoHeight: true,
            width: 900,

            items: this.getFormPanel(),

            buttons: [
                {
                    text: 'Enviar',
                    scope: this,
                    handler: this.toAsk
                },
                {
                    text: 'Cancelar',
                    scope: this,
                    handler: this.destroy
                }
            ]
        });

        common.document_access.control.changes.BaseJustification.superclass.constructor.call(this, cfg);
    }
});
