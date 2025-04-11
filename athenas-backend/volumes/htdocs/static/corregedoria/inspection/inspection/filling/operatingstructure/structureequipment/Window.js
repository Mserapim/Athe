Ext._define('corregedoria.inspection.inspection.filling.operatingstructure.structureequipment.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.inspection.inspection.filling.operatingstructure.structureequipment.Restful',

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
                        layout: 'form',
                        labelWidth: 77,
                        items: [
                            {
                                xtype: 'textfield',
                                fieldLabel: 'Equipamento',
                                name: 'equipment',
                                hideLabel: false,
                                width: 490,
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                labelWidth: 70,
                                columnWidth: 0.5,
                                layout: 'form',
                                items: [
                                    {
                                        xtype: 'numberfield',
                                        // xtype: 'textfield',
                                        fieldLabel: 'Quantidade',
                                        name: 'amount',
                                        hideLabel: false,
                                        allowBlank: true,
                                        // regex: /^[\d]+$/,
                                        // regexText: 'Entrada inválida. Campo permite apenas números.',
                                        width: 200,
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                labelWidth: 35,
                                columnWidth: 0.5,
                                layout: 'form',
                                items: [
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: 'Papel',
                                        hiddenName: 'status',
                                        width: 245,
                                        choiceId: 'inspection.STATUS_EQUIPMENT',
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
                                width: 490,
                                height: 50,
                            },
                        ]
                    },
                ]
            });

        return this._formPanel;
    },
});
