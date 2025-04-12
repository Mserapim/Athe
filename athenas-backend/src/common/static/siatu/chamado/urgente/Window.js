/**
 *
 **/
Ext._define('common.siatu.chamado.urgente.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.siatu.chamado.Restful',

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 60,
                items: [
                    // {
                    //     xtype: 'textfield',
                    //     name: 'urgente',
                    //     fieldLabel: 'Urgente',
                    //     allowBlank:false,
                    //     // hidden:true,
                    //     width: 250,
                    // },
                    {
                        xtype: 'textfield',
                        name: 'motivo_urgencia',
                        fieldLabel: 'Motivo',
                        allowBlank: true,
                        width: 250,
                    },

                ]
            });

        return this._formPanel;
    }
});
