Ext._define('corregedoria.prontuary.functionalperformance.inspectionlink.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.prontuary.functionalperformance.inspectionlink.Restful',

    width: 600,

    getInspectionField: function(cfg) {
        if(!this._inspectionField) {
            this._inspectionField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Inspeção/Correição",
                allowBlank: true,
                rest: "corregedoria.inspection.inspection.Restful",
                name: "inspection",
                disabled: false,
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar:['add', 'remove', 'filling', 'sign', 'menu', 'response', 'applyFilter', 'menuRecommendation', 'viewReport', '-'],
                    hideColumns: ['employee_unicode'],
                    hiddenFilter: true,
                    preFilter: [
                        {property: 'employee_id', value: cfg.values.employee_id, stage: 100},
                    ],
                }
            });
        }
        return this._inspectionField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 110,
                items: [
                    this.getInspectionField(cfg),
                    // {
                    //     xtype: 'checkbox',
                    //     name: 'active',
                    //     boxLabel: 'Vinculada ao Prontuário',
                    //     checked: false
                    // },
                ]
            });

        return this._formPanel;
    },
});
