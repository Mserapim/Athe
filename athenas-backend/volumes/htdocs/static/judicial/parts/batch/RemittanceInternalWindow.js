Ext._define('judicial.parts.batch.RemittanceInternalWindow', {
    extend: 'judicial.remittance.RemittanceInternalWindow',

    remittanceBatch: function (parameters) {
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Enviando procedimentos...' });
        
        mask.show();

        Ext.Ajax.request({
            url: core.callAction('EJudRemittanceInternal', 'remittance_batch'),
            params: parameters,
            method: 'POST',
            scope: this,
            callback: function () {
                mask.hide();
            },
            success: function (xhr) {
                var rst = Ext.decode(xhr.responseText);

                if (rst.success) {
                    this.destroy();
                    this.ownerGrid.getStore().load();
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
                    this.remittanceBatch(params);
                }
            });

        return this._registerButton;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        judicial.parts.batch.RemittanceInternalWindow.superclass.constructor.call(this, cfg);
    }
});
