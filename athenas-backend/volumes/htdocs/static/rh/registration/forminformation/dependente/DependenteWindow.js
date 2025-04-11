Ext._define('rh.registration.forminformation.dependente.DependenteWindow', {
    extend: 'core.RestfulWindow',

    rest: 'rh.registration.forminformation.dependente.DependenteRestful',
    height: 600,
    width: 600,
    
    constructor: function(cfg) {
        rh.registration.forminformation.dependente.DependenteWindow.superclass.constructor.call(this, cfg);
        this.getFormPanel(cfg);
    },

    trueOrFalse: function (value) {
        if (value == true)
            return false;
        else
            return true;
    },

    // validCPF: function(cpf){
    //         var Soma;
    //         var Resto;
    //         Soma = 0;
    //       if (cpf == "00000000000") return false;
        
    //       for (i=1; i<=9; i++) Soma = Soma + parseInt(cpf.substring(i-1, i)) * (11 - i);
    //       Resto = (Soma * 10) % 11;
        
    //         if ((Resto == 10) || (Resto == 11))  Resto = 0;
    //         if (Resto != parseInt(cpf.substring(9, 10)) ) return false;
        
    //       Soma = 0;
    //         for (i = 1; i <= 10; i++) Soma = Soma + parseInt(cpf.substring(i-1, i)) * (12 - i);
    //         Resto = (Soma * 10) % 11;
        
    //         if ((Resto == 10) || (Resto == 11))  Resto = 0;
    //         if (Resto != parseInt(cpf.substring(10, 11) ) ) return false;
    //         return true;
    //     },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                height: 600,
                width: 600,
                items: [
                    {
                        fieldLabel: 'Nome do dependente',
                        xtype: 'textfield',
                        hiddenName: 'nome_dependent',
                        name: 'nome_dependent',
                        enableKeyEvents: true,
                        width: 500,
                        disabled: this.trueOrFalse(cfg.values.nome_dependent_can_edit)
                    },
                    {
                        fieldLabel: 'Sexo do dependente',
                        xtype: 'combo',
                        hiddenName: 'sexo_dependent',
                        name: 'sexo_dependent',
                        enableKeyEvents: true,
                        allowBlank: true,
                        lazyRender: true,
                        mode: 'local',
                        triggerAction: 'all',
                        store: [
                            ['F', 'FEMININO'],
                            ['M', 'MASCULINO']
                        ],
                        width: 200,
                        disabled: true
                    },
                    {
                        xtype: 'cpffield',
                        width: 200,
                        enableKeyEvents: true,
                        name: 'cpf_dependent',
                        fieldLabel: 'CPF',
                        disabled: this.trueOrFalse(cfg.values.cpf_dependent_can_edit)
                    },
                    {
                        name: "data_nascimento_dependent",
                        fieldLabel: "Data de Nascimento",
                        xtype: "datefield",
                        allowBlank: true,
                        width: 140,
                        disabled: true
                    },
                    {

                        xtype: 'choicefield',
                        fieldLabel: "Tipo de Parentesco *",
                        hiddenName: 'grau_parentesco',
                        choiceId: 'rh.GRAU_PARENTESCO_CHOICES',
                        width: 450,
                        disabled: true,
                        hidden: true
                    },
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Tipo *',
                        hiddenName: 'tipo',
                        choiceId: 'rh.DEPENDENT_TYPE',
                        width: 450,
                        disabled: this.trueOrFalse(cfg.values.tipo_can_edit)
                    },
                    {
                        xtype: "checkbox",
                        boxLabel: "Incapacidade física/mental",
                        allowBlank: true,
                        hideLabel: true,
                        name: "incapacity",
                        checked: this.trueOrFalse(cfg.values.tipo_can_edit),
                        disabled: true

                    },
                ]
            });

        return this._formPanel;
    },



});

