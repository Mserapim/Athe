rh.employee.specialized.tab.fields.Graduation = Ext.extend(
    rh.employee.specialized.tab.fields.Field,
    {
        constructor: function(cfg) {
            rh.employee.specialized.tab.fields.Graduation.superclass.constructor.call(this, cfg);
        },

        observerEmployeePk: function(){
            rh.employee.specialized.tab.fields.Graduation.superclass.observerEmployeePk.call(this, {});
            this.getGraduationFieldSet().collapse(false);
            this.getImprovementFieldSet().collapse(false);
            this.getPublishedFieldSet().collapse(false);
        },

        fields: function(cfg){
            return [
                this.getGraduationFieldSet(),
                this.getImprovementFieldSet(),
                this.getPublishedFieldSet(),
            ];
        },

        getGraduationFieldSet: function(){
            if(!this._graduationFieldSet)
                this._graduationFieldSet = this._factoryFieldSet({title: 'Graduação', items:[this.getGraduation()], height: 350}, this.getGraduation());
            return this._graduationFieldSet;
        },

        getImprovementFieldSet: function(){
            if(!this._improvementFieldSet)
                this._improvementFieldSet = this._factoryFieldSet({title: 'Aperfeiçoamento e Pós-Graduação', items:[this.getImprovement()], height: 350}, this.getImprovement());
            return this._improvementFieldSet;
        },

        getPublishedFieldSet: function(){
            if(!this._publishedFieldSet)
                this._publishedFieldSet = this._factoryFieldSet({title: 'Trabalhos Publicados', items:[this.getPublished()], height: 350}, this.getPublished());
            return this._publishedFieldSet;
        },

        getGraduation: function(){
            if(!this._graduation)
                this._graduation = this._factoryGrid('rh.cnmp.GraduationCNMPGrid', {
                    gridAutoLoad: false,
                    height: 200,
                    scope: this,
                    callBeforeExpand: function(){
                        var employee = this.scope.myParams('employeePk');
                        if(employee != undefined){
                            this.setFilterProperty('employee__id', employee, 100);
                            this.setParam('employee', employee);
                            this.enable();
                        }
                        else{
                            this.removeFilterProperty('employee__id', 100);
                            this.setParam('employee', undefined);
                            this.disable();
                        }
                    }
                });
            return this._graduation;
        },

        getImprovement: function(){
            if(!this._improvement)
                this._improvement = this._factoryGrid('rh.cnmp.ImprovementAndGraduateCNMPGrid', {
                    gridAutoLoad: false,
                    height: 200,
                    scope: this,
                    callBeforeExpand: function(){
                        var employee = this.scope.myParams('employeePk');
                        if(employee != undefined){
                            this.setFilterProperty('employee__id', employee, 100);
                            this.setParam('employee', employee);
                            this.enable();
                        }
                        else{
                            this.removeFilterProperty('employee__id', 100);
                            this.setParam('employee', undefined);
                            this.disable();
                        }
                    }
                });
            return this._improvement;
        },

        getPublished: function(){
            if(!this._published)
                this._published = this._factoryGrid('rh.cnmp.PublishedWorksCNMPGrid', {
                    gridAutoLoad: false,
                    height: 200,
                    scope: this,
                    callBeforeExpand: function(){
                        var employee = this.scope.myParams('employeePk');
                        if(employee != undefined){
                            this.setFilterProperty('employee__id', employee, 100);
                            this.setParam('employee', employee);
                            this.enable();
                        }
                        else{
                            this.removeFilterProperty('employee__id', 100);
                            this.setParam('employee', undefined);
                            this.disable();
                        }
                    }
                });
            return this._published;
        },
    }
);
