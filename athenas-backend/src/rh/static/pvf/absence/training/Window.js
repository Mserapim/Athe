Ext._define('rh.pvf.absence.training.Window', {
    extend: 'rh.pvf.absence.absence.Window',

    rest: 'rh.pvf.absence.training.Restful',

    getCurseField: function (cfg) {
        if (!this._curse) {
            this._curse = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Curso',
                allowBlank: false,
                rest: 'rh.curso.Restful',
                name: 'curse',

            });
        }
        return this._curse;
    },

    getInstitutionField: function(cfg){
        if (!this._institution){
            this._institution = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: "Instituição",
                allowBlank: false,
                rest: "rh.administrativeunit.Restful",
                name: "institution"
            });
        }
        return this._institution;
    },

    getDays: function (cfg) {
        if (!this._days)
            this._days = Ext._create('Ext.form.NumberField', {
                width: 70,
                hideLabel: true,
                enableKeyEvents: true,
                value:90,
                readOnly:true,
                listeners: {
                    scope: this,
                    change: function (text, event) {
                        this.getEndDisplay();
                    }
                }
            });

        return this._days;
    },

    getStartDateField: function () {
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
                        this.getEndDisplay();
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
                        title: 'Início',
                        border: false,
                        width: 150,
                        defaults: {
                            defaults: { margins: '0 0 5 0' },
                        },
                        items: [
                            this.getStartDateField(),
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

    getEndDisplay: function () {
        if (this.getStartDateField().getValue() != '' && this.getDays().getValue() > 0) {
            data = Date.parseDate(this.getStartDateField().value, 'd/m/Y');
            data.setDate(data.getDate() + (parseInt(this.getDays().getValue() - 1)));
            this.getEndDate().setValue(Ext.util.Format.date(data, 'd/m/Y'));
        }
    },


    getGeneralInfoFieldSet: function (cfg) {
        if (!this._generalInfo)
            this._generalInfo = Ext._create('Ext.form.FieldSet', {
                title: 'Informações Gerais',
                items: [
                    //this.getEmployeeField(cfg),
                    this.getCurseField(),
                    this.getInstitutionField(),

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

