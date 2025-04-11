Ext._define('rh.pvf.absence.politicalactivity.Window', {
    extend: 'rh.pvf.absence.absence.Window',

    rest: 'rh.pvf.absence.politicalactivity.Restful',


    getElectiveOfficeField: function (cfg) {
        if (!this._electiveOfficeField) {
            this._electiveOfficeField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Cargo Eletivo',
                hiddenName: 'elective_office',
                choiceId: 'rh.CARGO_ELETIVO_CHOICES',
                anchor: '99%',
            });
        }
        return this._electiveOfficeField;

    },

    getLocationField: function (cfg) {
        if (!this._location) {
            this._location = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Localidade',
                allowBlank: false,
                rest: 'rh.localidade.Restful',
                name: 'location',
            });
        }
        return this._location;
    },

    getPoliticalPartyField: function (cfg) {
        if (!this._politicalPartyField)
            this._politicalPartyField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Partido Pol\u00edtico',
                name: 'political_party',
                allowBlank: false,
                maxLength: 100
            });

        return this._politicalPartyField;
    },

    getGeneralInfoFieldSet: function (cfg) {
        if (!this._generalInfo)
            this._generalInfo = Ext._create('Ext.form.FieldSet', {
                title: 'Informações Gerais',
                items: [
                    //this.getEmployeeField(cfg),
                    this.getElectiveOfficeField(),
                    this.getLocationField(),
                    this.getPoliticalPartyField(),

                ]
            });

        return this._generalInfo;
    },

    getFormItems: function (cfg) {
        return [
            this.getGeneralInfoFieldSet(),
            this.getDatesFieldSet(),
            this.getObservationFieldSet(),
        ];
    },
    
    save:function(cfg){
        var params = this.getFormPanel().getForm().getValues()
        substitutes_data = this.setStoreSubstitute(this.getSubstituteStore())
        params['substitutes'] = JSON.stringify(substitutes_data)
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Persistindo dados...'});  
        mask.show();
        rest.doRequest(
            rest.getRoute('save', false, 'POST', {
                scope: this,
                params,
                callback: function() {
                    mask.hide();
                    mask = undefined;
                },
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if(rst.success) {
                        this.ownerGrid.getStore().reload()
                        this.destroy();
                    }
                    else
                        Ext.Msg.show({
                            title: 'Atenção',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });
                },
                failure: function(xhr) {
                    Ext.Msg.show({
                        title: 'Atenção',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Recurso indisponível no momento.'
                    });
                },
            })
        ); 

    }


    // getFormPanel: function(cfg) {
    //     if(!this._formPanel)
    //         this._formPanel = Ext._create('Ext.form.FormPanel', {
    //             border: false,
    //             frame: true,
    //             items: [
    //             {
    //                 name: "created_by",
    //                 fieldLabel: "created by",
    //                 xtype: "rest-autocompletefield",
    //                 allowBlank: true,
    //                 rest: "auth.userRestful"
    //             },
    //             {
    //                 name: "modified_by",
    //                 fieldLabel: "modified by",
    //                 xtype: "rest-autocompletefield",
    //                 allowBlank: true,
    //                 rest: "auth.userRestful"
    //             },
    //             {
    //                 name: "created_at",
    //                 fieldLabel: "created at",
    //                 xtype: "tk-datetimefield",
    //                 allowBlank: true
    //             },
    //             {
    //                 name: "modified_at",
    //                 fieldLabel: "modified at",
    //                 xtype: "tk-datetimefield",
    //                 allowBlank: true
    //             },
    //             {
    //                 name: "employee",
    //                 fieldLabel: "employee",
    //                 xtype: "rest-autocompletefield",
    //                 allowBlank: false,
    //                 rest: "rh.servidorRestful"
    //             },
    //             {
    //                 name: "start_date",
    //                 fieldLabel: "Data In\u00edcio",
    //                 xtype: "datefield",
    //                 allowBlank: false
    //             },
    //             {
    //                 name: "end_date",
    //                 fieldLabel: "Data In\u00edcio",
    //                 xtype: "datefield",
    //                 allowBlank: false
    //             },
    //             {
    //                 name: "days",
    //                 fieldLabel: "Quantidade de dias",
    //                 xtype: "numberfield",
    //                 allowBlank: false,
    //                 allowDecimals: false
    //             },
    //             {
    //                 name: "observation",
    //                 fieldLabel: "Observa\u00e7\u00e3o",
    //                 xtype: "textfield",
    //                 allowBlank: false
    //             },
    //             {
    //                 name: "absence_ptr",
    //                 fieldLabel: "absence ptr",
    //                 xtype: "textfield",
    //                 allowBlank: false
    //             },
    //             {
    //                 name: "elective_office",
    //                 fieldLabel: "Cargo Eletivo",
    //                 xtype: "combo",
    //                 allowBlank: false,
    //                 hiddenName: "elective_office",
    //                 triggerAction: "all",
    //                 mode: "local",
    //                 store: [
    //                     [
    //                         1,
    //                         "Prefeito/Vice"
    //                     ],
    //                     [
    //                         2,
    //                         "Vereador"
    //                     ],
    //                     [
    //                         3,
    //                         "Deputado Estadual"
    //                     ],
    //                     [
    //                         4,
    //                         "Deputado Federal"
    //                     ],
    //                     [
    //                         5,
    //                         "Governador/Vice"
    //                     ],
    //                     [
    //                         6,
    //                         "Senador/Presidente Rep\u00fablica/Vice"
    //                     ]
    //                 ],
    //                 lazyRender: true
    //             },
    //             {
    //                 name: "political_party",
    //                 fieldLabel: "Partido Pol\u00edtico",
    //                 xtype: "textfield",
    //                 allowBlank: false,
    //                 maxLength: 100
    //             },
    //             {
    //                 name: "location",
    //                 fieldLabel: "location",
    //                 xtype: "rest-autocompletefield",
    //                 allowBlank: true,
    //                 rest: "rh.localidadeRestful"
    //             }
    //         ]
    //         });

    //     return this._formPanel;
    // }
});

