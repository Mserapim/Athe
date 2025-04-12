/**
 *
 **/
Ext._define('common.siatu.atendente.WindowNotificacao', {
    extend: 'core.RestfulWindow',

    rest: 'common.siatu.atendente.Restful',

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 55,
                items: [
                   {
                        xtype: 'checkbox',
                        boxLabel: 'Recebimento de chamado',
                        hideLabel: true,
                        name: 'notificacao_receber_chamado',
                    },
                ]
            });

        return this._formPanel;
    }
});
