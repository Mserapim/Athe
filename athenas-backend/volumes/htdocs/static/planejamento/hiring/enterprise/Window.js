Ext._define('planning.hiring.enterprise.Window', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.enterprise.Restful',

    width: 800,

    constants: {
        HAS_STRUCTURE: false,
        STRUCTURE: 5
    },

    getCorporateStructureGrid: function() {
        if(!this._corporateStructureGrid) {
            this._corporateStructureGrid = Ext._create('planning.hiring.corporatestructure.Grid', {
                title: 'Sócios',
                region: 'south',
                height: 300,
                gridAutoLoad: false
            });
        }

        return this._corporateStructureGrid;
    },

    observeEnterprise: function () {
        var value = this.enterprise();

        if (value) {
            // this.getCorporateStructureGrid().enable();
            this.getCorporateStructureGrid().setParam('enterprise', value);
            this.getCorporateStructureGrid().setFilterProperty('enterprise', value, 0);
        } else {
            // this.getCorporateStructureGrid().disable();
            this.getCorporateStructureGrid().setParam('enterprise', 0);
            this.getCorporateStructureGrid().setFilterProperty('enterprise', value, 0, false);
            this.getCorporateStructureGrid().getStore().removeAll();
        }
    },

    enterprise: function (value, observe) {
        observe = (observe === undefined ? true : observe);

        if (value !== undefined) {
            this._enterpriseGrid = value;

            if (observe)
                this.observeEnterprise();
        }

        return this._enterpriseGrid;
    },

    _motiveSelect: function (combo, record, index) {
        var value = combo.getValue();

        hiddenMotiveField = this.getFormPanel().getForm().findField("motive");

        hiddenMotiveField.setValue(value);
    },

    getMotiveField: function () {
        if (!this._motiveField)
            this._motiveField = Ext._create('standard.fields.ChoiceField', {
                width: 350,
                allowBlank: true,
                fieldLabel: "Motivo",
                name: "MOTIVO_ESTRUTURA",
                choiceId: "contrato.MOTIVO_ESTRUTURA",
                hiddenName: "motive_choice",
                listeners: {
                    scope: this,
                    select: this._motiveSelect,
                }
            });

        return this._motiveField;
    },

    _onApply: function (cfg, checked) {
        motiveField = this.getFormPanel().getForm().findField("motive_choice");
                
        if (checked == this.constants.HAS_STRUCTURE) {
            motiveField.disable();
            motiveField.setValue(this.constants.STRUCTURE);
            this.getCorporateStructureGrid().enable();
        } else {
            motiveField.enable();
            this.getCorporateStructureGrid().disable();
        }
    },

    getFormPanel: function(cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: "rest-autocompletefield",
                        name: "person",
                        fieldLabel: "Empresa",
                        width: 658,
                        allowBlank: false,
                        rest: "rh.person.Restful",
                    },
                    {
                        xtype: 'checkbox',
                        name: 'apply',
                        fieldLabel: "Não se aplica",
                        allowBlank: false,
                        listeners: {
                            scope: this,
                            check: this._onApply
                        },
                    },
                    this.getMotiveField(),
                    {
                        width: 350,
                        allowBlank: false,
                        hidden: true,
                        fieldLabel: "Motivo Escondido",
                        name: "motive",
                        xtype: "textfield"
                    },
                    this.getCorporateStructureGrid()
                ]
            });

        return this._formPanel;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function (instance) {
                    var value = instance.pk;
                    this.getCorporateStructureGrid().setParam('enterprise', value);
                    this.getCorporateStructureGrid().setFilterProperty('enterprise', value, 0);
                }
            }
        });
        this._onApply(null, false);
        planning.hiring.enterprise.Window.superclass.constructor.call(this, cfg);
        this.enterprise(cfg.oId === undefined ? null : cfg.oId);
    },
});
