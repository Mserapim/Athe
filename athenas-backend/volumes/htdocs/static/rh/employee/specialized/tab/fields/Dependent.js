rh.employee.specialized.tab.fields.Dependent = Ext.extend(
    rh.employee.specialized.tab.fields.Field,
    {
        constructor: function(cfg) {
            rh.employee.specialized.tab.fields.Dependent.superclass.constructor.call(this, cfg);
        },

        observerEmployeePk: function(){
            rh.employee.specialized.tab.fields.Dependent.superclass.observerEmployeePk.call(this, {});
            if(this.myParams('employeePk')){
                this.getDependentGrid().enable();
                this.getDependentGrid().setParam('servidor', this.myParams('employeePk'));
                this.getDependentGrid().setFilterProperty('servidor__pk', this.myParams('employeePk'), 100);

                this.getDependencyGrid().enable();
            }else{
                this.getDependentGrid().setParam('servidor', undefined);
                this.getDependentGrid().removeFilterProperty('servidor__pk', 100, false);
                this.getDependentGrid().disable();

                this.getDependencyGrid().disable();
            }
        },

        fields: function(cfg){
            var items = [
                this.getDependentGrid(),
                this.getDependencyGrid(),
            ];
            return items;
        },

        observeDependente: function() {
            if(this.dependente()){
                this.getDependencyGrid().enable();
                this.getDependencyGrid().setParam('dependente', this.dependente());
                this.getDependencyGrid().setFilterProperty('dependente_id', this.dependente(), 100);
            }
            else{
                this.getDependencyGrid().disable();
                this.getDependencyGrid().getStore().removeAll();
                this.getDependencyGrid().setFilterProperty('dependente_id', 0, 100, false);
            }
        },

        dependente: function(value, dispatch){
            dispatch = core.nullValue(dispatch, true);
            if(value !== undefined){
                this._dependente = value;

                if(dispatch) this.observeDependente();
            }
            else
                return this._dependente;
        },

        getDependentGrid: function(cfg) {
            if(!this._dependentGrid) {
                this._dependentGrid = Ext._create('rh.dependente.DependenteGrid',{
                    hideItemsToolbar: ['search', 'download'],
                    title: 'Dependentes',
                    region: 'center',
                    border: false,
                    scope: this,
                    height: 300,
                    gridAutoLoad: false,
                    columnAction: false,
                    hideColumns: [
                        'unicode',
                        'auxilio_creche',
                        'data_alteracao',
                        'data_fim',
                        'motivo_inicio_dependencia',
                        'motivo_inicio_dependencia_display',
                        'motivo_fim_dependencia',
                        'motivo_fim_dependencia_display',
                        'data_cadastro',
                        'dep_ir',
                        'data_inicio',
                        'dep_sf',
                        'dependente_direto',
                        'responsavel_unicode',
                    ]
                });
                this._dependentGrid.getSelectionModel().on({
                    scope: this,
                    rowselect: function(sm, index, data){
                        this.dependente(data.get('pk'));
                    },
                    rowdeselect: function(){
                        this.dependente(null);
                    },
                });
                this._dependentGrid.getStore().on({
                    scope: this,
                    load: function(gd, opts){
                        var selection = this._dependentGrid.getSelectionModel();
                        var rec = selection.getSelected();
                        this.dependente(null);
                        if(rec){
                            selection.clearSelections();
                            selection.selectRecords([rec]);
                        }

                    }
                });
            }
            return this._dependentGrid;
        },

        getDependencyGrid: function(cfg) {
            if(!this._dependencyGrid) {
                this._dependencyGrid = Ext._create('rh.dependente.DependenciaGrid',{
                    hideItemsToolbar: ['search', 'download'],
                    title: 'Dependência',
                    region: 'center',
                    border: false,
                    scope: this,
                    height: 400,
                    columnAction: false,
                    gridAutoLoad: false,
                    hideColumns: [
                        'unicode',
                    ]
                });
            }
            return this._dependencyGrid;
        },

    }
);
