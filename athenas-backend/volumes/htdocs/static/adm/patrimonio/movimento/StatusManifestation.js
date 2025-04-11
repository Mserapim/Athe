/**
 *
 **/
Ext._define('adm.patrimonio.movimento.StatusManifestation', {
    extend: 'Ext.Window',

    width: 650,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: false,
                layout: 'fit',
                items: [
                    Ext._create('toolkit.fields.CKEditor', {
                        name: 'comentario',
                        height: 300
                    })
                ]
            });

        return this._formPanel;
    },

    batchStateChange: function() {
        rest = Ext._create('adm.patrimonio.movimento.LogStatusRestful');

        rest.manifestateStatusChange(
            {
                pkset: this.params.movimentos,
                status: this.params.status,
                comentario: this.getFormPanel().getForm().getValues().comentario
            },
            {
                scope: this,
                fn: function(result) {
                    Ext.Msg.show({
                        title: 'Alterando estado de Movimentação.',
                        icon: result.success ? Ext.Msg.INFO : Ext.Msg.ERROR,
                        msg: result.message,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Alterando estado de Movimentação',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function(result) {
                    core.invokeCallback(this.callback.success);
                    this.destroy();
                }
            }
        );
    },

    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        Ext.apply(cfg, {
            autoHeight: true,
            width: 500,
            modal: true,

            items: this.getFormPanel(),

            buttons: [
                {
                    text: 'Salvar',
                    scope: this,
                    handler: this.batchStateChange
                },
                {
                    text: 'Cancelar',
                    scope: this,
                    handler: this.destroy
                }
            ]
        });

        adm.patrimonio.movimento.StatusManifestation.superclass.constructor.call(this, cfg);
    }
});
