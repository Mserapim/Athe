Ext._define('corregedoria.inspection.inspection.filling.attachments.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.inspection.inspection.filling.attachments.Restful',

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
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 35,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: 'Área',
                                        hiddenName: 'area',
                                        width: 230,
                                        choiceId: 'inspection.AREA',
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 35,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: 'Tipo',
                                        hiddenName: 'attachment_type',
                                        width: 230,
                                        choiceId: 'inspection.ATTACHMENT_TYPE',
                                    },
                                ]
                            },
                        ]
                    },
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
