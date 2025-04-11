Ext._define('rh.employee.trainee.Window', {
    extend: 'rh.employee.Window',

    rest: 'rh.employee.trainee.Restful',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        if (cfg && cfg.ownerGrid && cfg.ownerGrid.matriculaFieldBlocked) {
            this.setMatriculaFieldBlocked(cfg.ownerGrid.matriculaFieldBlocked);
        }

        Ext.applyIf(cfg, {
            width: 700,
            height: 620,
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
        rh.employee.trainee.Window.superclass.constructor.call(this, cfg);
        this._observe();
    },

    setMatriculaFieldBlocked: function(matriculaFieldBlocked){
        this.matriculaFieldBlocked = matriculaFieldBlocked;
    },

    getMatriculaFieldBlocked: function(){
        return this.matriculaFieldBlocked;
    },

    _observe: function() {
        var grid;

        if(this.matricula){
            if(this.getFormPanel().getForm().findField('matricula').getValue() == ""){
                this.getFormPanel().getForm().findField('matricula').setValue(this.matricula);
            }
        }

        if(this.oId) {
            grid = this.getDeclarationActivityGrid();
            grid.setParam('servidor', this.oId);
            grid.setFilterProperty('servidor', this.oId, 1001)
            grid.enable();
        }
        else {
            grid = this.getDeclarationActivityGrid();
            grid.setParam('servidor', 0);
            grid.setFilterProperty('servidor', 0, 1001, false);
            grid.getStore().removeAll();
            grid.disable();
        }
    },

    getMatriculaParamsField: function() {
        var matriculaParams = {
            xtype: 'textfield',
            fieldLabel: 'Matrícula',
            name: 'matricula'
        };
        if(this.getMatriculaFieldBlocked() === 'true'){
            matriculaParams['disabled'] = true;
            matriculaParams['readOnly'] = true;
        }
        return matriculaParams;
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
                        fieldLabel: 'Estagiário *',
                        name: 'pessoa_fisica',
                        displayField: 'unicode',
                        allowBlank: false,
                        rest: 'rh.person.naturalperson.Restful',
                    },
                    this.getMatriculaParamsField(),
                    {
                        xtype: 'combo',
                        fieldLabel: 'Tipo',
                        allowBlank: false,
                        lazyRender: true,
                        hiddenName: 'tipo',
                        mode: 'local',
                        triggerAction: 'all',
                        store: [
                            ['I', 'INDEFINIDO'],
                            ['E', 'ESTAGIÁRIO'],
                            ['M', 'MEMBRO DO MINISTÉRIO PÚBLICO'],
                            ['P', 'MILITAR'],
                            ['S', 'SERVIDOR'],
                            ['T', 'TERCEIRIZADO'],
                            ['V', 'VOLUNTÁRIO'],
                        ],
                        name: 'tipo',
                        value: 'E',
                        readOnly: true
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Supervisor',
                        name: 'employee_supervisor',
                        displayField: 'unicode',
                        allowBlank: true,
                        rest: 'rh.employee.Restful',
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Instituição de Educação',
                        name: 'educational_institution',
                        displayField: 'unicode',
                        allowBlank: true,
                        rest: 'rh.person.legalperson.Restful'
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Agente de Integração',
                        name: 'integration_agent',
                        displayField: 'unicode',
                        allowBlank: true,
                        rest: 'rh.person.legalperson.Restful'
                    },
                    {
                        xtype: 'textfield',
                        fieldLabel: 'Área de ocupação',
                        name: 'occupation_area',
                        maxLength: 50,
                    },
                    this.getNatureChoiceField(cfg),
                    this.getLevelChoiceField(cfg),
                    {
                        xtype: 'textfield',
                        fieldLabel: 'Número de seguro',
                        name: 'insurance_number',
                        maxLength: 50,
                    },
                    {
                        xtype: 'textfield',
                        fieldLabel: 'Valor',
                        name: 'value',
                        xtype: 'numberfield',
                    },
                    this.getDeclarationActivityGrid(cfg)
                ],

            });

        return this._formPanel;
    },

    getDeclarationActivityGrid: function(cfg) {
        if(!this._declarationActivityGrid){
            this._declarationActivityGrid = Ext._create('rh.declarationactivity.Grid', {
                title: 'Declaração de Atividade',
                region: 'center',
                gridAutoLoad: false,
                minHeight: 150,
                height: 200,
                oId: cfg.oId
            });
        }
        return this._declarationActivityGrid;
    },

    getNatureChoiceField: function(cfg) {
        if (!this._natureChoiceField) {
            this._natureChoiceField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Natureza *',
                hiddenName: 'nature',
                choiceId: 'rh.TRAINEE_NATURE',
            });
        }
        return this._natureChoiceField;
    },

    getLevelChoiceField: function(cfg) {
        if (!this._levelChoiceField) {
            this._levelChoiceField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Nível *',
                hiddenName: 'level',
                choiceId: 'rh.TRAINEE_LEVEL',
            });
        }
        return this._levelChoiceField;
    }

});
