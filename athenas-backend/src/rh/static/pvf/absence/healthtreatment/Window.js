Ext._define('rh.pvf.absence.healthtreatment.Window', {
    extend: 'rh.pvf.absence.absence.Window',

    rest: 'rh.pvf.absence.healthtreatment.Restful',

    getMedicalCertificateField: function () {
        if (!this._medicalCertificateField) {
            this._medicalCertificateField = Ext._create('core.fields.FileUploadField', {
                name: 'medical_certificate',
                fieldLabel: 'Atestado Médico',
                allowBlank: true,
                width: 500,
            });
        }

        return this._medicalCertificateField;
    },


    getCIDField: function () {
        if (!this._cidField)
            this._cidField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'CID',
                name: 'cid',
                rest: 'rh.afastamento.cid.Restful',
                gridColumnAction: false,
                gridConfig: {
                    configOrderToolBar: ['search', '->'],
                    columnAction: false,
                    onlyColumns:['cid_code','description'],
                }

            });

        return this._cidField;
    },


    getGeneralInfoFieldSet: function (cfg) {
        if (!this._generalInfo)
            this._generalInfo = Ext._create('Ext.form.FieldSet', {
                title: 'Informações Gerais',
                items: [
                    //this.getEmployeeField(cfg),
                    this.getMedicalCertificateField(),
                    this.getCIDField(),
                ]
            });

        return this._generalInfo;
    },

    getDays: function (cfg) {
        if (!this._days)
            this._days = Ext._create('Ext.form.NumberField', {
                width: 70,
                fieldLabel: "Dias",
                enableKeyEvents: true,
                listeners: {
                    scope: this,
                    change: function (text, event) {
                        this.getEndDisplay(cfg);
                    }
                }
            });

        return this._days;
    },

    getHours: function (cfg) {
        if (!this._hours)
            this._hours = Ext._create('Ext.form.NumberField', {
                width: 70,
                fieldLabel: "Horas",
                enableKeyEvents: true,
                hidden:cfg.params.type_employee == "M"?true:false,
                listeners: {
                    scope: this,
                    change: function (text, event) {
                        this.getEndDisplay(cfg);
                    }
                }
            });

        return this._hours;
    },

    getStartDateField: function (cfg) {
        if (!this._startDateField) {
            this._startDateField = new Ext.form.DateField({
                hideLabel: true,
                format: 'd/m/Y',
                width: 120,
                name:"start_date",
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
                        title: 'Data Início',
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
                        title: 'Tempo Afastado',
                        border: false,
                        width: 300,
                        items: [
                            this.getDays(cfg),
                            this.getHours(cfg),
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
        if (this.getStartDateField().getValue() != '' && (this.getDays().getValue() > 0 || this.getHours().getValue() > 0 )) {
            var days = 0
            if (this.getDays().getValue() > 0 ){
                days = parseInt(this.getDays().getValue() - 1)
            }
            data = Date.parseDate(this.getStartDateField().value, 'd/m/Y');
            data.setDate(data.getDate() + days);
            this.getEndDate().setValue(Ext.util.Format.date(data, 'd/m/Y'));
            if (cfg.params.responsible){
                this.setSubstituteFilter(cfg, this.getStartDateField().getValue())
                this.getSubstitutePanel().enable()
            }
        }
        if (this.getDays().getValue() > 0){
            this.getHours().disable();
        }else{
            this.getHours().enable();
        }
        if (this.getHours().getValue() > 0){
            this.getDays().disable();
        }else{
            this.getDays().enable();
        }

    },

    getFormItems: function (cfg) {
        return [
            this.getGeneralInfoFieldSet(),
            
            this.getDatesFieldSet(cfg),
            {
                xtype: 'fieldset',
                border: false,
                layout: 'anchor',
                hidden:cfg.params.type_employee == "M"?true:false,
                defaults: {
                    anchor: '100%',
                    style: {
                        fontWeight: 'bold'
                    }
                },
                items: [
                    {
                        xtype: 'displayfield',
                        value: '* Para afastamento com menos de um dia, deve preencher somente o campo Horas',
                        margin: '0 0 0 0'
                    }
                ]
            },
            this.getObservationFieldSet(),
        ];
    },

    

    save:function(cfg){
        var params = this.getFormPanel().getForm().getValues()
        substitutes_data = this.setStoreSubstitute(this.getSubstituteStore())
        params['substitutes'] = JSON.stringify(substitutes_data)
        params['end_date'] = this.getEndDate().getValue()
        params['days'] = this.getDays().getValue()
        params['hours'] = this.getHours().getValue()
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

