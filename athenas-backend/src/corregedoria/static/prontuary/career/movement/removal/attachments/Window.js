Ext._define('corregedoria.prontuary.career.movement.removal.attachments.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.prontuary.career.movement.removal.attachments.Restful',

    width: 600,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        labelWidth: 55,
                        layout: 'form',
                        items: [
                            {
                                xtype: 'textfield',
                                fieldLabel: 'Descrição',
                                name: 'description',
                                hideLabel: false,
                                width: 495,
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 45,
                        items: [
                            {
                                xtype: 'ged-fileuploadfield',
                                fieldLabel: 'Arquivo',
                                allowBlank: true,
                                name: 'attached_file',
                                hiddenName: 'attached_file'
                            },
                        ]
                    },
                ]
            });

        return this._formPanel;
    },
});
