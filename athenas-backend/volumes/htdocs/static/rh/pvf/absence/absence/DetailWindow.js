Ext._define('rh.pvf.absence.absence.DetailWindow', {
    extend: 'rh.pvf.portalrequest.DetailWindow',
    rest: 'rh.pvf.absence.absence.Restful',

    height:650,
    width:1050,


    getFieldSet:function(cfg){
        return this.getAbsenceFieldSet(cfg)
    },

    getAbsenceFieldSet: function (cfg) {
        if (!this._marked)
            this._marked = Ext._create('Ext.form.FieldSet', {
                title: 'Dados Licença/Afastamento',
                items: [
                    {
                        xtype: 'panel',
                        layout: 'column',
                        items:[
                            { 
                                columnWidth: .27,
                                layout: 'form',
                                items: [
                                    {
                                        name: "start_date_absence",
                                        fieldLabel: "Data Início",
                                        xtype: "datefield",
                                        allowBlank: false,
                                        width:150,
                                        readOnly:true,
                                        value:cfg.data.start_date_absence
                                    },
                                    {
                                        name: "end_date_absence",
                                        fieldLabel: "Data Fim",
                                        xtype: "datefield",
                                        allowBlank: false,
                                        readOnly:true,
                                        width:150,
                                        value:cfg.data.end_date_absence
                                    },
                                    {
                                        name: "days_absence",
                                        fieldLabel: "Quantidade de dias",
                                        xtype: "numberfield",
                                        allowBlank: false,
                                        width:150,
                                        readOnly:true,
                                        value:cfg.data.days_absence
                                    },
                                    {
                                        name: "hours",
                                        fieldLabel: "Quantidade de horas afastado",
                                        xtype: "numberfield",
                                        allowBlank: false,
                                        width:150,
                                        readOnly:true,
                                        value:cfg.data.hours
                                    },
                            ]},  
                            { 
                                columnWidth: .73,
                                layout: 'form',
                                items: [
                                    {
                                        name: "get_medical_certificate",
                                        fieldLabel: "Atestado Médico",
                                        xtype: "core-fileuploadfield",
                                        allowBlank: false,
                                        width:250,
                                        hidden:cfg.data.get_medical_certificate?cfg.data.is_request_substitute?true:false:true,
                                        readOnly:true,
                                        value:cfg.data.get_medical_certificate
                                    },
                                    {
                                        xtype: 'rest-autocompletefield',
                                        rest: 'rh.afastamento.cid.Restful',
                                        name: "cid",
                                        fieldLabel: "CID",
                                        allowBlank: true,
                                        width:250,
                                        hidden:cfg.data.get_medical_certificate?false:true,
                                        readOnly:true,
                                        value:cfg.data.cid
                                    },
                                    {
                                        name: "get_blood_donation_comprovation",
                                        fieldLabel: "Comprovante de Doação",
                                        xtype: "core-fileuploadfield",
                                        allowBlank: false,
                                        width:250,
                                        hidden:cfg.data.get_blood_donation_comprovation?false:true,
                                        readOnly:true,
                                        value:cfg.data.get_blood_donation_comprovation
                                    },
                                    {
                                        xtype: 'rest-autocompletefield',
                                        fieldLabel: 'Familiar',
                                        allowBlank: false,
                                        rest: 'rh.person.naturalperson.Restful',
                                        name: 'person',
                                        width:250,
                                        hidden:cfg.data.dependent_family?false:true,
                                        readOnly:true,
                                        value:cfg.data.dependent_family
                                    },
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: 'Grau de Parentesco',
                                        allowBlank: false,
                                        lazyRender: true,
                                        readOnly:true,
                                        hidden:cfg.data.degree_kinship?false:true,
                                        hiddenName: 'degree_kinship',
                                        choiceId: 'rh.GRAU_PARENTESCO_CHOICES',
                                        name: 'degree_kinship',
                                        value:cfg.data.degree_kinship
                                    },
                                    {
                                        xtype: 'rest-autocompletefield',
                                        fieldLabel: 'Instituição',
                                        allowBlank: false,
                                        rest: 'rh.administrativeunit.Restful',
                                        name: 'institution',
                                        width:250,
                                        hidden:cfg.data.institution?false:true,
                                        readOnly:true,
                                        value:cfg.data.institution
                                    },
                                    {
                                        xtype: 'rest-autocompletefield',
                                        fieldLabel: 'Curso',
                                        allowBlank: false,
                                        rest: 'rh.curso.Restful',
                                        name: 'curse',
                                        width:250,
                                        hidden:cfg.data.curse?false:true,
                                        readOnly:true,
                                        value:cfg.data.curse
                                    },
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: 'Cargao Eletivo',
                                        allowBlank: false,
                                        lazyRender: true,
                                        readOnly:true,
                                        width:250,
                                        hidden:cfg.data.elective_office?false:true,
                                        hiddenName: 'elective_office',
                                        choiceId: 'rh.CARGO_ELETIVO_CHOICES',
                                        name: 'elective_office',
                                        value:cfg.data.elective_office
                                    },
                                    {
                                        xtype: 'rest-autocompletefield',
                                        fieldLabel: 'Localidade',
                                        allowBlank: false,
                                        rest: 'rh.localidade.Restful',
                                        name: 'location',
                                        width:250,
                                        hidden:cfg.data.location?false:true,
                                        readOnly:true,
                                        value:cfg.data.location
                                    },
                                    {
                                        name: "political_party",
                                        fieldLabel: "Partido Político",
                                        xtype: "textfield",
                                        allowBlank: false,
                                        readOnly:true,
                                        hidden:cfg.data.political_party?false:true,
                                        readOnly:true,
                                        width:250,
                                        value:cfg.data.political_party
                                    },
                                    {
                                        xtype: 'rest-autocompletefield',
                                        fieldLabel: 'Dependente',
                                        allowBlank: false,
                                        rest: 'rh.pvf.person.Restful',
                                        name: 'dependent',
                                        width:300,
                                        hidden:cfg.data.dependent?false:true,
                                        readOnly:true,
                                        value:cfg.data.dependent
                                    },
                                    {
                                        name: "birth_certificate",
                                        fieldLabel: "Certidão de Nascimento",
                                        xtype: "core-fileuploadfield",
                                        allowBlank: false,
                                        width:250,
                                        hidden:cfg.data.birth_certificate?false:true,
                                        readOnly:true,
                                        value:cfg.data.birth_certificate
                                    },
                                    {
                                        xtype: "checkbox",
                                        boxLabel: "Dependente Auxílio Creche?",
                                        allowBlank: true,
                                        hideLabel: true,
                                        checked: cfg.data.is_childcare_assistence,
                                        name: "is_childcare_assistence",
                                        hidden:cfg.data.is_childcare_assistence?false:true,
                                        readOnly:true,
                                    },
                                    {
                                        xtype: "checkbox",
                                        boxLabel: "Dependente do Imposto de Renda?",
                                        allowBlank: true,
                                        hideLabel: true,
                                        checked:cfg.data.is_incoming_tax,
                                        name: "is_incoming_tax",
                                        hidden:cfg.data.is_incoming_tax?false:true,
                                        readOnly:true,
                                        disabled:true,
                                    },
                                    {
                                        xtype: "choicefield",
                                        allowBlank: true,
                                        hideLabel: true,
                                        lazyRender: true,
                                        name: "dependent_type",
                                        choiceId: 'rh.DEPENDENT_TYPE',
                                        hidden:cfg.data.dependent_type?false:true,
                                        readOnly:true,
                                        value:cfg.data.dependent_type,
                                        width:720,
                                        disabled:true,
                                    },
                                    {
                                        name: "death_certificate",
                                        fieldLabel: "Atestado de óbito",
                                        xtype: "core-fileuploadfield",
                                        allowBlank: false,
                                        width:250,
                                        hidden:cfg.data.death_certificate?false:true,
                                        readOnly:true,
                                        value:cfg.data.death_certificate
                                    },
                                    {
                                        xtype: 'rest-autocompletefield',
                                        fieldLabel: 'Familiar',
                                        allowBlank: false,
                                        rest: 'rh.person.naturalperson.Restful',
                                        name: 'person',
                                        width:250,
                                        hidden:cfg.data.person?false:true,
                                        readOnly:true,
                                        value:cfg.data.person
                                    },
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: 'Tipo de Vínculo',
                                        allowBlank: false,
                                        lazyRender: true,
                                        readOnly:true,
                                        width:250,
                                        hidden:cfg.data.family_bond?false:true,
                                        hiddenName: 'family_bond',
                                        choiceId: 'rh.GRAU_PARENTESCO_CHOICES',
                                        name: 'elective_office',
                                        value:cfg.data.family_bond
                                    },

                                    {
                                        name: "marriage_certificate",
                                        fieldLabel: "Certidão de Casamento(Civil)",
                                        xtype: "core-fileuploadfield",
                                        allowBlank: false,
                                        width:250,
                                        hidden:cfg.data.marriage_certificate?false:true,
                                        readOnly:true,
                                        value:cfg.data.marriage_certificate
                                    },
                                    {
                                        xtype: 'rest-autocompletefield',
                                        fieldLabel: 'Parceiro',
                                        allowBlank: false,
                                        rest: 'rh.person.naturalperson.Restful',
                                        name: 'person',
                                        width:250,
                                        hidden:cfg.data.person_partner?false:true,
                                        readOnly:true,
                                        value:cfg.data.person_partner
                                    },
                                    
                                   
                            ]},
                         
        
                        ]
                    },    
                   
                   
                ]
            });

        return this._marked;
    },


});