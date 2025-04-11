Ext._define('planning.hiring.supervisor.SupervisorWindow', {
    extend: 'core.RestfulWindow',
    rest: 'planning.hiring.supervisor.SupervisorRestful',
    width: 480,

    relatedName: undefined,

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.supervisor(instance.pk);
                    this.oId = instance.pk;
                    this.action = 'update';
                }
            }
        });

        planning.hiring.supervisor.SupervisorWindow.superclass.constructor.call(this, cfg);
        this.supervisor(cfg.oId === undefined ? null : cfg.oId);
    },

    supervisor: function(value, observe) {
        observe = (observe === undefined ? true : observe);

        if (value !== undefined) {
            this._supervisorGrid = value;

            if (observe)
                this.observeSupervisor();
        }

        return this._supervisorGrid;
    },

    observeSupervisor: function() {
        var value = this.supervisor();

        if (value)
            this.getSuperVisorClassificationField().objectId(value);
    },

    getSuperVisorClassificationField: function(cfg) {
        if (!this._supervisorClassification)
            this._supervisorClassification = Ext._create('core.fields.RelatedRestfulField', {
                title: 'Classificação',
                hideLabel: true,
                name: 'classifications',
                displayField: 'unicode',
                allowBlank: false,
                relatedname: this.relatedName,
                rest: this.rest,
                sourceRest: 'planning.hiring.supervisor.ClassificationRestful',
                oId: this.oId || cfg.oId,
                width: 455,
                height: 190,
                border: false
            });

        return this._supervisorClassification;
    },

    getEmployeeField: function() {
        if (!this._employee) {
            this._employee = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: "Fiscal",
                allowBlank: false,
                rest: "rh.employee.Restful",
                name: "employee",
                preFilter: [
                    {property: 'ativo__in', value: [true], stage: 1001},
                    {property: 'tipo__in', value: ['M', 'S'], stage: 1002}
                ]
            });

        }

        return this._employee;
    },

    getFormPanel: function(cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    this.getEmployeeField(),
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Tipo',
                        hiddenName: 'kind',
                        choiceId: 'contrato.SUPERVISOR_KIND',
                        width: 345
                    },
                    this.getSuperVisorClassificationField(cfg),
                    {
                        xtype: "textfield",
                        fieldLabel: 'Portaria',
                        name: 'publication_document',
                    },
                    {
                        xtype: "datefield",
                        fieldLabel: 'Data da Portaria',
                        name: 'publication_document_date',
                    },
                    {
                        xtype: "datefield",
                        allowBlank: true,
                        fieldLabel: "Data Início",
                        name: "begin"
                    },
                ]
            });
        }

        return this._formPanel;
    }
});
