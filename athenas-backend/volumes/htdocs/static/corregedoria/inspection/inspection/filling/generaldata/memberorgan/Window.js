Ext._define('corregedoria.inspection.inspection.filling.generaldata.memberorgan.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.inspection.inspection.filling.generaldata.memberorgan.Restful',

    width: 800,

    getEmployeeField: function() {
        if(!this._employeeField) {
            this._employeeField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: 'Membro',
                allowBlank: true,
                rest: "raf.EmployeeRestful",
                name: "employee",
                disabled: false,
                preFilter: [
                    {property: 'tipo', value: 'M', stage: 100},
                ],
                gridConfig: {
                    columnAction: false,
                    hideColumns: ['departure_unicode', 'effective_unicode', 'commission_unicode', 'elective_unicode', 'ativo'],
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                }
            });
        }
        return this._employeeField;
    },

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
                        labelWidth: 50,
                        items: [
                            this.getEmployeeField(cfg)
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
                                labelWidth: 35,
                                columnWidth: 0.80,
                                items: [
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: 'Papel',
                                        hiddenName: 'member_role',
                                        width: 555,
                                        choiceId: 'inspection.MEMBER_ROLE',
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 1,
                                columnWidth: 0.20,
                                items: [
                                    {
                                        xtype: 'checkbox',
                                        name: 'exclusive',
                                        boxLabel: 'Atuação exclusiva',
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
                                labelWidth: 1,
                                columnWidth: 0.25,
                                items: [
                                    {
                                        xtype: 'checkbox',
                                        name: 'needs_exclusivity',
                                        boxLabel: 'Necessita de exclusividade',
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                labelWidth: 70,
                                layout: 'form',
                                columnWidth: 0.75,
                                items: [
                                    {
                                        xtype: 'textarea',
                                        fieldLabel: 'Jutificativa',
                                        name: 'justify',
                                        hideLabel: false,
                                        allowBlank: true,
                                        width: 500,
                                        height: 50,
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
                                width: 687,
                                height: 50,
                            },
                        ]
                    },
                ]
            });

        return this._formPanel;
    },
});
