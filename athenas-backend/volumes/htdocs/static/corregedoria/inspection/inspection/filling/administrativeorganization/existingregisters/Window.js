Ext._define('corregedoria.inspection.inspection.filling.administrativeorganization.existingregisters.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.inspection.inspection.filling.administrativeorganization.existingregisters.Restful',

    width: 650,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                labelWidth: 70,
                                columnWidth: 0.65,
                                layout: 'form',
                                items: [
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 50,
                                        items: [
                                            {
                                                xtype: 'textfield',
                                                fieldLabel: 'Registro',
                                                name: 'register',
                                                hideLabel: false,
                                                width: 335,
                                            },
                                        ]
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                labelWidth: 70,
                                columnWidth: 0.35,
                                layout: 'form',
                                items: [
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        labelWidth: 30,
                                        layout: 'form',
                                        items: [
                                            {
                                                xtype: 'choicefield',
                                                fieldLabel: 'Tipo',
                                                hiddenName: 'registration_type',
                                                width: 180,
                                                choiceId: 'inspection.REGISTRATION_TYPE',
                                            },
                                        ]
                                    },
                                ]
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        labelWidth: 77,
                        layout: 'form',
                        items: [
                            {
                                xtype: 'textarea',
                                fieldLabel: 'Observações',
                                name: 'observation',
                                hideLabel: false,
                                allowBlank: true,
                                width: 540,
                                height: 50,
                            },
                        ]
                    },
                ]
            });

        return this._formPanel;
    },
});
