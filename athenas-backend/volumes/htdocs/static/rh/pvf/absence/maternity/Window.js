Ext._define('rh.pvf.absence.maternity.Window', {
    extend: 'rh.pvf.absence.absence.Window',

    rest: 'rh.pvf.absence.maternity.Restful',

    height: 600,
    width: 755,

    getDependentField: function (cfg) {
        if (!this._familiarField)
            this._familiarField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Dependente',
                name: 'dependent',
                rest: 'rh.pvf.person.ChildRestful',
                gridColumnAction: false,
                enableKeyEvents: true,
                comboListeners: {
                    scope: this,
                    select: {
                        buffer: 1,
                        fn: function(field, record) {
                            this.getDependentDisplay(record,cfg);
                        }
                    },
                }
            });

        return this._familiarField;
    },

    getBirthCertificateField: function () {
        if (!this._birthCertificateField) {
            this._birthCertificateField = Ext._create('core.fields.FileUploadField', {
                name: 'birth_certificate',
                fieldLabel: 'Certidão de Nascimento',
                allowBlank: true,
                width: 500,
            });
        }

        return this._birthCertificateField;
    },

    getChildCareAssistenceField: function (cfg) {
        if (!this._urgencyField) {
            this._urgencyField = Ext._create('Ext.form.Checkbox', {
                name: 'is_childcare_assistence',
                hideLabel: true,
                hidden:cfg.params.type_employee == "M"?true:false,
                boxLabel: 'Dependente Auxílio Creche?'
            });
        }

        return this._urgencyField;
    },

    getIncomingTaxField: function (cfg) {
        if (!this._incomingTaxField) {
            this._incomingTaxField = Ext._create('Ext.form.RadioGroup', {

                items: [
                    { boxLabel: 'Dependente de Imposto de Renda?', name: 'is_incoming_tax', inputValue: true, checked: true},
                    { boxLabel: 'Não dependente de Imposto de Renda?', name: 'is_incoming_tax', inputValue: false,},
                ],
                name: 'is_incoming_tax',
                hideLabel: true,
            });
        }

        return this._incomingTaxField;
    },

    getDependentTypeField: function (cfg) {
        if (!this._dependentTypeField) {
            this._dependentTypeField = Ext._create('standard.fields.ChoiceField', {
                xtype: 'choicefield',
                name: 'dependent_type',
                hideLabel: true,                                        
                choiceId: 'rh.DEPENDENT_TYPE',
                width: 680,
            });
            var store = this._dependentTypeField.getStore();
            var filter = Ext.decode(store.baseParams.filter);
            filter.push({ property: 'value__in', value: [3, 4], stage: 1 });
            store.baseParams.filter = Ext.encode(filter);
            store.load();
        }

        return this._dependentTypeField;
    },    

    getDays: function (cfg) {
        if (!this._days)
            this._days = Ext._create('Ext.form.NumberField', {
                width: 70,
                hideLabel: true,
                enableKeyEvents: true,
                value:180,
                readOnly:true,
                listeners: {
                    scope: this,
                    change: function (text, event) {
                        this.getEndDisplay(cfg);
                    }
                }
            });

        return this._days;
    },

    getStartDateField: function (cfg) {
        if (!this._startDateField) {
            this._startDateField = new Ext.form.DateField({
                hideLabel: true,
                format: 'd/m/Y',
                width: 120,
                name:"start_date",
                readOnly : true,
                maxValue:(new Date()).format('d/m/Y'),
                enableKeyEvents: true,
                listeners: {
                    scope: this,
                    change: function (text, event) {
                        this.getEndDisplay(cfg);
                    }
                }
            });
        }
        return this._startDateField;
    },

    getDatesFieldSet: function(cfg){
        if (!this._datesFieldSet){
            this._datesFieldSet = Ext._create('Ext.form.FieldSet', {
                title: 'Informe as datas',
                layout: 'hbox',
                items: [
                    {
                        xtype: 'fieldset',
                        title: 'Data Nascimento',
                        border: false,
                        width: 150,
                        defaults: {
                            defaults: { margins: '0 0 5 0' },
                        },
                        items: [
                            this.getStartDateField(cfg),
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        title: 'Dias',
                        border: false,
                        width: 100,
                        items: [
                            this.getDays(cfg)
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        title: 'Fim',
                        border: false,
                        width: 100,
                        items: [
                            this.getEndDate(),
                        ]
                    },
                    
                ]
            });
        }

        return this._datesFieldSet;
    },

    getEndDate: function () {
        if (!this._enddate)
            this._enddate = Ext._create('Ext.form.DisplayField', {
                hideLabel: true,
                name:"end_date",
                height: 18
            });

        return this._enddate;
    },

    getEndDisplay: function (cfg) {
        if (this.getStartDateField().getValue() != '' && this.getDays().getValue() > 0) {
            data = Date.parseDate(this.getStartDateField().value, 'd/m/Y');
            data.setDate(data.getDate() + (parseInt(this.getDays().getValue() - 1)));
            this.getEndDate().setValue(Ext.util.Format.date(data, 'd/m/Y'));
        }
    },

    getDependentDisplay: function (record,cfg) {

        if (record.data.data_nascimento != '' && record.data.data_nascimento != undefined) {
            data = Ext.util.Format.date(record.data.data_nascimento, 'd/m/Y')
            this.getStartDateField().setValue(data);
            this.getEndDisplay();
            if (cfg.params.responsible){
                this.setSubstituteFilter(cfg, this.getStartDateField().getValue())
                this.getSubstitutePanel().enable()
            }

        } else{
            Ext.Msg.show({
                title: 'Atenção',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'O dependente não possui data de nascimento cadastrada.'
            });
        }
    },

    getGeneralInfoFieldSet: function (cfg) {
        if (!this._generalInfo)
            this._generalInfo = Ext._create('Ext.form.FieldSet', {
                title: 'Informações Gerais',
                // hidden: cfg.action == "create" ? false : true,
                items: [
                    //this.getEmployeeField(cfg),
                    this.getBirthCertificateField(cfg),
                    this.getDependentField(cfg),
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Capacidade',
                        hiddenName: 'capacity',
                        choiceId: 'rh.CAPACITY',
                        anchor: '99%',
                    },
                    this.getChildCareAssistenceField(cfg),
                    {
                        xtype: 'fieldset',
                        title: 'IR',
                        layout: 'hbox',
                        defaults: {
                            xtype: 'panel',
                            flex: 1.0,
                            layout: 'form',
                            labelAlign: 'top'
                        },
                        items: [
                            {
                                items: [
                                    this.getIncomingTaxField(cfg),
                                    this.getDependentTypeField(cfg),
                                ]
                            },
                        ]
                    },
                 
                    // {
                    //     xtype: "checkbox",
                    //     boxLabel: "Incapacidade física/mental",
                    //     allowBlank: true,
                    //     hideLabel: true,
                    //     name: "incapacity",
                    //     checked: false,
                    // },

                ]
            });

        return this._generalInfo;
    },

    getFormItems: function (cfg) {
        return [
            this.getGeneralInfoFieldSet(cfg),
            this.getDatesFieldSet(cfg),
            this.getObservationFieldSet(),
        ];
    },

    _observer: function(enable) {
        if(enable) {
            this.getDependentTypeField().enable();
        }
        else {
            this.getDependentTypeField().disable();
        }
    },

    save:function(cfg){
        var params = this.getFormPanel().getForm().getValues()
        substitutes_data = this.setStoreSubstitute(this.getSubstituteStore())
        params['substitutes'] = JSON.stringify(substitutes_data)
        params['end_date'] = this.getEndDate().getValue()
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
});

