Ext._define('corregedoria.prontuary.individualperformance.performanceparticulardifficulty.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.prontuary.individualperformance.performanceparticulardifficulty.Restful',

    width: 630,

    getEmployeeLocationField: function(cfg) {
        if(!this._employeeLocationField) {
            this._employeeLocationField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Exercício",
                allowBlank: true,
                rest: "rh.employee.workplace.Restful",
                name: "employeelocation",
                disabled: false,
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar:['add', 'remove', 'edit', 'download', '-', 'setMain'],
                    hideColumns: ['icons', 'servidor_unicode', 'chefe_imediato_unicode', 'chefe_lotacao_unicode' ],
                    hiddenFilter: true,
                    params: {designacao: true, servidor_id: cfg.values.employee_id},
                    preFilter: [
                        {property: 'servidor_id', value: cfg.params.employee_id, stage: 100},
                        {property: 'designacao', value: true, stage: 101},
                    ],
                }
            });
            this._employeeLocationField.getComboField().setPreFilter([
                {property: 'servidor_id', value: cfg.params.employee_id, stage: 100},
                {property: 'designacao', value: true, stage: 101},
            ]);
        }
        return this._employeeLocationField;
    },

    getListIndicationField: function(cfg) {
        if(!this._listIndicationField) {
            this._listIndicationField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Edital",
                allowBlank: true,
                rest: "corregedoria.prontuary.individualperformance.listindication.Restful",
                name: "used_edital",
                disabled: false,
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar:['add', 'remove', 'edit', 'download', '-',],
                    hideColumns: ['icons',],
                    hiddenFilter: true,
                    preFilter: [
                        {property: 'listindication__prontuary_id', value: cfg.params.prontuary, stage: 100},
                        {property: 'list_figuration', value: 2, stage: 101},
                    ],
                }
            });
        }
        return this._listIndicationField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 110,
                items: [
                    this.getEmployeeLocationField(cfg),
                    this.getListIndicationField(cfg),
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.getFormPanel().getForm().setValues(instance);
                    this.oId = instance.pk;
                    this.action = 'update';
                }
            }
        });
        corregedoria.prontuary.individualperformance.performanceparticulardifficulty.Window.superclass.constructor.call(this, cfg);
    },

});
