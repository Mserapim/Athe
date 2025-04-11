Ext._define('judicial.parts.batch.ScientifyWorkplaceWindow', {
    extend: 'judicial.ScientifyWorkplaceWindow',

    rest: 'judicial.ScientifyWorkplaceRestful',

    width: 750,

    saveBatch: function (parameters) {
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Salvando documento nos procedimentos...' });

        mask.show();

        Ext.Ajax.request({
            url: core.callAction('EJudScientifyWorkplace', 'save_batch'),
            params: parameters,
            method: 'POST',
            scope: this,
            callback: function () {
                mask.hide();
            },
            success: function (xhr) {
                var rst = Ext.decode(xhr.responseText);
                this.ownerGrid.getStore().reload();
                if (rst.success) {
                    this.destroy();
                    Ext.Msg.show({
                        title: 'Movimentação de procedimentos em bloco',
                        msg: rst.message,
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK
                    });
                }
                else
                    Ext.Msg.show({
                        title: 'Erro na movimentação de procedimentos em bloco',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function () {
                Ext.Msg.show({
                    title: 'Falha',
                    msg: 'Falha na movimentação. Nenhum procedimento foi modificado.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    getButtons: function (cfg) {
        if (!this._buttons) {
            this._buttons = [];
            this._buttons.push({
                text: 'Salvar',
                scope: this,
                handler: function () {
                    params = Ext.applyIf(
                        this.getFormPanel().getForm().getValues(),
                        this.getParams()
                    )
                    this.saveBatch(params);
                }
            });
            this._buttons.push(
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            );

        }
        return this._buttons;
    }

});
