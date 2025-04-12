Ext._define('judicial.parts.batch.RemittanceExternalWindow', {
    extend: 'judicial.remittance.RemittanceInternalWindow',

    remittanceBatch: function (parameters) {
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Enviando procedimentos...' });
        
        mask.show();

        Ext.Ajax.request({
            url: core.callAction('EJudRemittanceExternal', 'remittance_batch'),
            params: parameters,
            method: 'POST',
            scope: this,
            callback: function () {
                mask.hide();
            },
            success: function (xhr) {
                var rst = Ext.decode(xhr.responseText);

                if (rst.success) {
                    this.ownerGrid.getStore().load();
                    this.destroy();
                    Ext.Msg.show({
                        title: 'Envio de procedimentos em bloco',
                        msg: rst.message,
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK
                    });
                }
                else
                    Ext.Msg.show({
                        title: 'Erro no envio de procedimentos em bloco',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function () {
                Ext.Msg.show({
                    title: 'Falha',
                    msg: 'Falha no envio de procedimentos. Nenhum procedimento foi enviado.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    registerButton: function (cfg) {
        if (!this._registerButton)
            this._registerButton = Ext._create('Ext.Button', {
                text: 'Registrar',
                scope: this,
                handler: function() {
                    params = Ext.applyIf(
                        this.getFormPanel().getForm().getValues(),
                        this.getParams()
                    )
                    console.log(params);
                    this.remittanceBatch(params);
                }
            });

        return this._registerButton;
    },

    getRemitToField: function () {
        if (!this._remitToField) {
            this._remitToField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: "Remeter para",
                allowBlank: true,
                rest: "rh.generalorgan.Restful",
                name: "organ",
                emptyText: 'Selecione um órgão para registrar o envio',
                preFilter: [
                    { property: 'lotacao', value: null, stage: 1000 }
                ]
            });
        }

        return this._remitToField;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        judicial.parts.batch.RemittanceExternalWindow.superclass.constructor.call(this, cfg);
    }
});
