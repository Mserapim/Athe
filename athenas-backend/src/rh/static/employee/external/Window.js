Ext._define('rh.employee.external.Window', {
    extend: 'rh.employee.Window',

    rest: 'rh.employee.external.Restful',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        if (cfg && cfg.ownerGrid && cfg.ownerGrid.matriculaFieldBlocked) {
            this.setMatriculaFieldBlocked(cfg.ownerGrid.matriculaFieldBlocked);
        }

        Ext.applyIf(cfg, {
            width: 700,
            height: 440,
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
        rh.employee.external.Window.superclass.constructor.call(this, cfg);
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
                height: 380,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Pessoa Física',
                        name: 'pessoa_fisica',
                        displayField: 'unicode',
                        allowBlank: false,
                        rest: 'rh.person.naturalperson.Restful'
                    },
                    this.getMatriculaParamsField(),
                    {
                        xtype: 'datefield',
                        fieldLabel: 'Ref. férias',
                        name: 'data_referencia_ferias',
                        format: 'd/m/Y'
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Chefe Imediato',
                        name: 'chefe_imediato',
                        displayField: 'unicode',
                        allowBlank: true,
                        rest: 'rh.employee.Restful'
                    },
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
                            ['A', 'JOVEM CIDADÃO - APRENDIZ'],
                            ['X', 'EXTERNO SEM VÍNCULO'],
                        ],
                        name: 'tipo',
                        value: 'X',
                        readOnly: true
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

});
