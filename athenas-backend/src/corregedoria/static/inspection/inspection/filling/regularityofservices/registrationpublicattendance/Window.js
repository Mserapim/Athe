Ext._define('corregedoria.inspection.inspection.filling.regularityofservices.registrationpublicattendance.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.inspection.inspection.filling.regularityofservices.registrationpublicattendance.Restful',

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
                                                allowBlank: true,
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
                                                allowBlank: true,
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
                                                allowBlank: true,
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
                                                allowBlank: true,
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
                                                allowBlank: true,
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
                                                allowBlank: true,
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
                                                allowBlank: true,
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
                                                allowBlank: true,
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
                                                allowBlank: true,
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
                                                allowBlank: true,
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
                                                allowBlank: true,
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
                                                allowBlank: true,
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
