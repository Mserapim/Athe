Ext._define('corregedoria.inspection.inspection.filling.structure.structurecommissionedemployees.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.inspection.inspection.filling.structure.structurecommissionedemployees.Restful',

    width: 600,

    getCommissionedEmployeesField: function(cfg) {
        if(!this._commissionedEmployeesField) {
            this._commissionedEmployeesField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Servidor Comissionado",
                allowBlank: true,
                rest: "corregedoria.inspection.inspection.filling.structure.personalmovement.CommissionedRestful",
                name: "commissioned_employee",
                disabled: false,
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar:['add', 'edit', 'remove', '-', 'download'],
                    params: {inspection: cfg.values.inspection_id},
                }
            });
        }
        return this._commissionedEmployeesField;
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
                        labelWidth: 130,
                        items: [
                            this.getCommissionedEmployeesField(cfg),
                        ]
                    },
                ]
            });

        return this._formPanel;
    },
});
