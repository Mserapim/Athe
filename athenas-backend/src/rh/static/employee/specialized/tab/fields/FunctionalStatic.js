rh.employee.specialized.tab.fields.FunctionalStatic = Ext.extend(
    rh.employee.specialized.tab.fields.Field,
    {
        constructor: function (cfg) {
            rh.employee.specialized.tab.fields.FunctionalStatic.superclass.constructor.call(this, cfg);
            this._observe(cfg);
        },

        _observe: function (cfg){
            if (cfg.employeePk === undefined || cfg.employeePk === -1){
                this.getSocialSecurity().disable()
            }

        },

        observerEmployeePk: function(){
            rh.employee.specialized.tab.fields.Move.superclass.observerEmployeePk.call(this, {});
            if (this.myParams('employeePk')) {
                this.getSocialSecurity().enable();
                this.getSocialSecurity().setParam('employee', this.myParams('employeePk'));
                this.getSocialSecurity().setFilterProperty('employee__id', this.myParams('employeePk'), 100);
            } else {
                this.getSocialSecurity().setParam('employee', undefined);
                this.getSocialSecurity().setFilterProperty('employee__id', 0, 100);
                this.getSocialSecurity().disable();
            }
        },

        fields: function () {
            return [
                this.SocialSecurityFieldSet(),
                this.InformationFieldSet(),
                this.EfectiveFieldSet(),
                this.commissionFieldSet(),
                this.ElectiveFieldSet(),
            ]
            
        },

        SocialSecurityFieldSet: function () {
            if(!this._ssecurityFieldSet)
                this._ssecurityFieldSet = this._factoryFieldSet(
                    {
                        title: 'Configurações previdenciárias',
                        collapsed: false,
                        autoWidth: true,
                        autoHeight: true,
                        items:[
                            this.getSocialSecurity()], 
                    }, this.getSocialSecurity());
            return this._ssecurityFieldSet;
        },

        getSocialSecurity: function(){
            if(!this._ssecurity)
                this._ssecurity = this._factoryGrid('rh.socialsecurity.SocialSecurityEmployeeGrid', {
                    callBeforeExpand: function(){
                        var employee = this.scope.myParams('employeePk');
                        if(employee != undefined){
                            this.setFilterProperty('employee__id', employee, 100);
                            this.setParam('employee', employee);
                            this.enable();
                        }
                        else{
                            this.setParam('employee', undefined);
                            this.setFilterProperty('employee__id', 0, 100);
                            this.disable();
                        }
                    }
                });
            return this._ssecurity;
        },

        InformationFieldSet: function () {
            return Ext._create('Ext.form.FieldSet', {
                title: 'Informações',
                collapsible: true,
                collapsed: false,
                autoWidth: true,
                autoHeight: true,
                labelAlign: 'left',
                defaults: { anchor: '-20' },
                defaultType: 'displayfield',
                items: [
                    {
                        name: 'employee_status',
                        xtype: 'displayfield',
                        fieldLabel: 'Estado',
                        readOnly: true
                    },
                    {
                        name: 'type_by_possession_display',
                        xtype: 'displayfield',
                        fieldLabel: 'Categoria',
                        readOnly: true
                    },
                    {
                        name: 'situation_functional_information',
                        xtype: 'displayfield',
                        fieldLabel: 'Situação Funcional',
                        readOnly: true
                    },
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Lotação',
                        readOnly: true,
                        value: 'Verificar menu Athenas >> Gestão de Pessoas >> Afastamento e Exercícios >> Servidor - Lotação e Exercícios'
                    },
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Exercício',
                        value: 'Verificar menu Athenas >> Gestão de Pessoas >> Afastamento e Exercícios >> Servidor - Lotação e Exercícios',
                        readOnly: true,
                    },
                    {
                        name: 'probationary_stage_information',
                        xtype: 'displayfield',
                        fieldLabel: 'Estágio Probatório',
                        readOnly: true
                    },
                    {
                        name: 'date_stability_information',
                        xtype: 'displayfield',
                        fieldLabel: 'Estabilidade',
                        readOnly: true
                    }
                ]
            });
        },

        EfectiveFieldSet: function () {
            return Ext._create('Ext.form.FieldSet', {
                title: 'Efetivo',
                collapsible: true,
                collapsed: false,
                autoWidth: true,
                autoHeight: true,
                labelAlign: 'left',
                defaults: { anchor: '-20' },
                defaultType: 'displayfield',
                items: [
                    {
                        name: 'job_position_efective',
                        xtype: 'displayfield',
                        fieldLabel: 'Cargo',
                        readOnly: true
                    },
                    {
                        name: 'progression_efective',
                        xtype: 'displayfield',
                        fieldLabel: 'Progressão atual',
                        readOnly: true
                    }
                ]
            });
        },

        commissionFieldSet: function () {
            return Ext._create('Ext.form.FieldSet', {
                title: 'Comissão/Função',
                collapsible: true,
                collapsed: false,
                autoWidth: true,
                autoHeight: true,
                labelAlign: 'left',
                defaults: { anchor: '-20' },
                defaultType: 'displayfield',
                items: [
                    {
                        name: 'job_position_commission',
                        xtype: 'displayfield',
                        fieldLabel: 'Cargo',
                        readOnly: true
                    },
                    {
                        name: 'reference_commission',
                        xtype: 'displayfield',
                        fieldLabel: 'Referência',
                        readOnly: true
                    }
                ]
            });
        },

        ElectiveFieldSet: function () {
            return Ext._create('Ext.form.FieldSet', {
                title: 'Eletivo',
                collapsible: true,
                collapsed: false,
                autoWidth: true,
                autoHeight: true,
                labelAlign: 'left',
                defaults: { anchor: '-20' },
                defaultType: 'displayfield',
                items: [
                    {
                        name: 'job_position_elective',
                        xtype: 'displayfield',
                        fieldLabel: 'Cargo',
                        readOnly: true
                    },
                    {
                        name: 'reference_elective',
                        xtype: 'displayfield',
                        fieldLabel: 'Referência',
                        readOnly: true
                    }
                ]
            });
        },
    }
);
