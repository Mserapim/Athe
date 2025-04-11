/**
 *
 **/
Ext._define('rh.pessoa.fisica.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.person.naturalperson.Restful',

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.getTabComplementar().find('name', 'endereco')[0].objectId(instance.pk);
                    this.getTabComplementar().find('name', 'telefone')[0].objectId(instance.pk);

                    this.oId = instance.pk;
                    this.action = 'update';
                }
            }
        });

        rh.pessoa.fisica.Window.superclass.constructor.call(this, cfg);
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                autoWidth: true,
                items: [
                    {
                        xtype: 'textfield',
                        name: 'nome',
                        fieldLabel: 'Nome',
                        allowBlank: false,
                        width: 300,
                    },
                    {
                        xtype: "combo",
                        fieldLabel: "Sexo",
                        allowBlank: true,
                        lazyRender: true,
                        hiddenName: "sexo",
                        mode: "local",
                        triggerAction: "all",
                        store: [
                            ["M", "MASCULINO"],
                            ["F", "FEMININO"]
                        ],
                        name: "sexo",
                        width: 300,
                    },
                    {
                        allowBlank: true,
                        fieldLabel: "Nascimento",
                        name: "data_nascimento",
                        xtype: "datefield",
                        width: 300,
                    },
                    {
                        maxLength: 20,
                        allowBlank: true,
                        fieldLabel: "RG",
                        name: "rg",
                        xtype: "textfield",
                        width: 300,
                    },
                    {
                        maxLength: 10,
                        allowBlank: true,
                        fieldLabel: "RG - Órgão",
                        name: "rg_orgao",
                        xtype: "textfield",
                        width: 300,
                    },
                    {
                        allowBlank: true,
                        fieldLabel: "RG - Expedição",
                        name: "rg_data_expedicao",
                        xtype: "datefield",
                        width: 300,
                    },
                    {
                        xtype: 'textfield',
                        name: 'cpf',
                        fieldLabel: 'CPF',
                        maxLength: 14,
                        allowBlank: true,
                        width: 300,
                        maskRe: /^[0-9.-]*$/
                    },
                    {
                        maxLength: 80,
                        allowBlank: true,
                        fieldLabel: "Pai",
                        name: "nome_pai",
                        xtype: "textfield",
                        width: 300,
                    },
                    {
                        maxLength: 80,
                        allowBlank: true,
                        fieldLabel: "Mãe",
                        name: "nome_mae",
                        xtype: "textfield",
                        width: 300,
                    },
                    {
                        xtype: "combo",
                        fieldLabel: "Estado civil",
                        allowBlank: false,
                        lazyRender: true,
                        hiddenName: "estado_civil",
                        mode: "local",
                        triggerAction: "all",
                        store: [
                            [1, "SOLTEIRO"],
                            [2, "CASADO"],
                            [3, "VIUVO"],
                            [4, "SEPARADO JUDICIALMENTE"],
                            [5, "DIVORCIADO"],
                            [6, "UNIAO ESTAVEL"],
                            [7, "NÃO FOI DEFINIDO NO CADASTRO"]
                        ],
                        name: "estado_civil",
                        width: 300,
                    },
                    {
                        xtype: "combo",
                        fieldLabel: "Raça/Cor",
                        allowBlank: false,
                        lazyRender: true,
                        hiddenName: "raca_cor",
                        mode: "local",
                        triggerAction: "all",
                        store: [
                            [6, "BRANCA"],
                            [1, "PARDA"],
                            [2, "AMARELA"],
                            [3, "PRETA"],
                            [4, "INDÍGENA"],
                            [5, "NÃO INFORMADO"]
                        ],
                        name: "raca_cor",
                        width: 300,
                    },
                    {
                        xtype: "combo",
                        fieldLabel: "Instrução",
                        allowBlank: true,
                        lazyRender: true,
                        hiddenName: "grau_instrucao",
                        mode: "local",
                        triggerAction: "all",
                        store: [
                            [1, "ANALFABETO"],
                            [2, "ALFABETIZADO SEM CURSOS REGULARES"],
                            [3, "FUNDAMENTAL INCOMPLETO"],
                            [4, "FUNDAMENTAL COMPLETO"],
                            [5, "MÉDIO INCOMPLETO"],
                            [6, "MÉDIO COMPLETO"],
                            [13, "TÉCNICO"],
                            [7, "SUPERIOR INCOMPLETO"],
                            [8, "SUPERIOR COMPLETO OU EQUIVALENTE LEGAL"],
                            [9, "ESPECIALIZAÇÃO/PÓS-GRADUAÇÃO"],
                            [10, "MESTRADO"],
                            [11, "DOUTORADO"],
                            [12, "PÓS-DOUTORADO"],
                            [14, "INFORMADO"]
                        ],
                        name: "grau_instrucao",
                        width: 300,
                    }
                ]
            });

        return this._formPanel;
    },
});
