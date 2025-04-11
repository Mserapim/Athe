Ext._define('corregedoria.inspection.inspection.filling.procuratorate.proceduralmovementreturned.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.inspection.inspection.filling.procuratorate.proceduralmovementreturned.Restful',

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
                        labelWidth: 65,
                        items: [
                            {
                                xtype: "numberfield",
                                fieldLabel: "Ano",
                                name: "year",
                                width: 100,
                                allowBlank: false,
                            },
                        ]
                    },
                    {
                        xtype:'fieldset',
                        title: 'Atendimentos registrados mensalmente',
                        collapsible: false,
                        autoHeight:true,
                        width: 570,
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
                                        labelWidth: 65,
                                        columnWidth: 0.33,
                                        items: [
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Janeiro",
                                                name: "amount_january",
                                                width: 100,
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 65,
                                        columnWidth: 0.33,
                                        items: [
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Fevereiro",
                                                name: "amount_february",
                                                width: 100,
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 65,
                                        columnWidth: 0.34,
                                        items: [
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Março",
                                                name: "amount_march",
                                                width: 100,
                                            },
                                        ]
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
                                        layout: 'form',
                                        labelWidth: 65,
                                        columnWidth: 0.33,
                                        items: [
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Abril",
                                                name: "amount_april",
                                                width: 100,
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 65,
                                        columnWidth: 0.33,
                                        items: [
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Maio",
                                                name: "amount_may",
                                                width: 100,
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 65,
                                        columnWidth: 0.34,
                                        items: [
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Junho",
                                                name: "amount_june",
                                                width: 100,
                                            },
                                        ]
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
                                        layout: 'form',
                                        labelWidth: 65,
                                        columnWidth: 0.33,
                                        items: [
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Julho",
                                                name: "amount_july",
                                                width: 100,
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 65,
                                        columnWidth: 0.33,
                                        items: [
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Agosto",
                                                name: "amount_august",
                                                width: 100,
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 65,
                                        columnWidth: 0.34,
                                        items: [
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Setembro",
                                                name: "amount_september",
                                                width: 100,
                                            },
                                        ]
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
                                        layout: 'form',
                                        labelWidth: 65,
                                        columnWidth: 0.33,
                                        items: [
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Outubro",
                                                name: "amount_october",
                                                width: 100,
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 65,
                                        columnWidth: 0.33,
                                        items: [
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Novembro",
                                                name: "amount_november",
                                                width: 100,
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 65,
                                        columnWidth: 0.34,
                                        items: [
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Dezembro",
                                                name: "amount_december",
                                                width: 100,
                                            },
                                        ]
                                    },
                                ]
                            },
                        ]
                    },
                ]
            });

        return this._formPanel;
    },
});
