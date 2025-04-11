Ext._define('corregedoria.inspection.inspection.filling.structure.structureeffectiveemployees.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.inspection.inspection.filling.structure.structureeffectiveemployees.Restful',

    width: 600,

    getEffetiveEmployeesField: function(cfg) {
        if(!this._effetiveEmployeesField) {
            this._effetiveEmployeesField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Servidor Efetivo",
                allowBlank: true,
                rest: "corregedoria.inspection.inspection.filling.structure.personalmovement.EffetiveRestful",
                name: "effective_employee",
                disabled: false,
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar:['add', 'edit', 'remove', '-', 'download'],
                    params: {inspection: cfg.values.inspection_id},
                }
            });
        }
        return this._effetiveEmployeesField;
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
                        labelWidth: 95,
                        items: [
                            this.getEffetiveEmployeesField(cfg),
                        ]
                    },
                ]
            });
        return this._formPanel;
    },
});
