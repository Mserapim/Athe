rh.employee.specialized.tab.fields.Resume = Ext.extend(
    rh.employee.specialized.tab.fields.Field,
    {
        constructor: function(cfg) {
            rh.employee.specialized.tab.fields.Resume.superclass.constructor.call(this, cfg);
        },

        observerEmployeePk: function(){
            rh.employee.specialized.tab.fields.Resume.superclass.observerEmployeePk.call(this, {});
            this.getResumeFieldSet().collapse(false);
        },

        fields: function(cfg){
            return [
                this.getResumeFieldSet(),
            ];
        },

        getResumeFieldSet: function(){
            if(!this._professionalExperienceFieldSet)
                this._professionalExperienceFieldSet = this._factoryFieldSet({title: 'Experiência Profissional', items:[this.getResume()], height: 350}, this.getResume());
            return this._professionalExperienceFieldSet;
        },

        getResume: function(){
            if(!this._professionalExperience)
                this._professionalExperience = this._factoryGrid('rh.carreira.experiencia_profissional.Grid', {
                    gridAutoLoad: false,
                    height: 200,
                    scope: this,
                    callBeforeExpand: function(){
                        var employee = this.scope.myParams('employeePk');
                        var naturalPerson = this.scope.myParams('naturalPersonPk');
                        if(employee != undefined){
                            this.setFilterProperty('servidor__id', employee, 100);
                            this.setParam('servidor', employee);
                            this.enable();
                        }
                        else{
                            this.removeFilterProperty('servidor__id', 100);
                            this.setParam('servidor', undefined);
                            this.disable();
                        }
                    }
                });
            return this._professionalExperience;
        },

    }
);
