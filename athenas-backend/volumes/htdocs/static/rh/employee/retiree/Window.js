Ext._define('rh.employee.retiree.Window', {
    extend: 'rh.employee.Window',

    rest: 'rh.employee.retiree.Restful',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            width: 700,
            height: 380,
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.oId = instance.pk;
                    this.matricula = instance.matricula;
                    this.action = 'update';
                    this._observe();
                }
            }
        });
        rh.employee.retiree.Window.superclass.constructor.call(this, cfg);
        this._observe();
    },

    _observe: function() {
        var grid;

        if(this.matricula){
            if(this.getFormPanel().getForm().findField('matricula').getValue() == ""){
                this.getFormPanel().getForm().findField('matricula').setValue(this.matricula);
            }
        }

        if(this.oId) {
            grid = this.getDeclarationActivityRetireeGrid();
            grid.setParam('servidor', this.oId);
            grid.setFilterProperty('servidor', this.oId, 1001)
            grid.enable();
        }
        else {
            grid = this.getDeclarationActivityRetireeGrid();
            grid.setParam('servidor', 0);
            grid.setFilterProperty('servidor', 0, 1001, false);
            grid.getStore().removeAll();
            grid.disable();
        }
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                height: 580,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Servidor Aposentado *',
                        name: 'pessoa_fisica',
                        displayField: 'unicode',
                        allowBlank: false,
                        rest: 'rh.person.naturalperson.Restful',
                    },
                    {
                        xtype: 'textfield',
                        fieldLabel: 'Nova matrícula *',
                        name: 'matricula',
                    },
                    this.getTypeRetirementChoiceField(),
                    {
                        xtype: 'combo',
                        fieldLabel: 'Tipo Anterior',
                        allowBlank: false,
                        lazyRender: true,
                        hiddenName: 'previous_type_display',
                        mode: 'local',
                        triggerAction: 'all',
                        store: rh.INDICATIVO,
                        name: 'previous_type',
                        value: '',
                        readOnly: true,
                        disabled: true
                    },
                    this.getDeclarationActivityRetireeGrid(cfg)
                ]
            });
        return this._formPanel;
    },

    getDeclarationActivityRetireeGrid: function(cfg) {
        if(!this._declarationActivityRetireeGrid){
            this._declarationActivityRetireeGrid = Ext._create('rh.declarationactivityretiree.Grid', {
                title: 'Declaração de Atividade',
                region: 'center',
                gridAutoLoad: false,
                minHeight: 150,
                height: 200,
                oId: cfg.oId
            });
        }
        return this._declarationActivityRetireeGrid;
    },

    getTypeRetirementChoiceField: function() {
        if (!this._typeRetirementChoiceField) {
            this._typeRetirementChoiceField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Tipo de Aposentadoria',
                hiddenName: 'type_retirement',
                choiceId: 'rh.TYPE_RETIREMENT',
                disabled: true
            });
        }
        return this._typeRetirementChoiceField;
    },
});