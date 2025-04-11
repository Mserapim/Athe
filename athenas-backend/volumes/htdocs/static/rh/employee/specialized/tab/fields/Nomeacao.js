
rh.employee.specialized.tab.fields.Nomeacao = Ext.extend(
    rh.employee.specialized.tab.fields.Field,
    {
        constructor: function (cfg) {
            rh.employee.specialized.tab.fields.Nomeacao.superclass.constructor.call(this, cfg);
        },

        observerNaturalPersonPk: function () {
            
            var natural_person = this.myParams('naturalPersonPk')
            
            // this.getNomeacaoGrid().setParam('natural_person', this.myParams('naturalPersonPk'));

            rh.employee.specialized.tab.fields.Nomeacao.superclass.observerNaturalPersonPk.call(this, {});
            this.getNomeacaoGrid().setFilterProperty('natural_person__id', this.myParams('naturalPersonPk'), 100);
            
            this.getNomeacaoGrid().setParam('employee', this.myParams('employeePk'));
            
            this.observerNomeacaoPk(null);
        },

        observerNomeacaoPk: function (pk) {
            var employeePk = this.myParams('employeePk');

            if (pk != undefined) {
                this.getNomeacaoAnexoGrid().setParam('convite', pk);
                this.getNomeacaoAnexoGrid().setFilterProperty('convite__id', pk, 100, true);
                this.getNomeacaoAnexoGrid().enable();
            } else {
                this.getNomeacaoAnexoGrid().setParam('convite', undefined);
                this.getNomeacaoAnexoGrid().setFilterProperty('convite__id', 0, 100, false);
                this.getNomeacaoAnexoGrid().disable();
            }
        },




        fields: function (cfg) {
            return [
                this.getNomeacaoGrid(cfg),
                this.getNomeacaoAnexoGrid(cfg),
            ];
        },

        getNomeacaoGrid: function (cfg) {
            if (!this._nomeacaoGrid) {
                this._nomeacaoGrid = Ext._create('rh.nomeacao.Grid', {
                    region: 'center',
                    hideItemsToolbar: ['search', 'download'],
                    border: false,
                    height: 200,
                    gridAutoLoad: true,
                    canEditCpfRg: false,
                    messageToUser: 'Utilize os campos da aba Dados Funcionais'
                });
                this._nomeacaoGrid.getSelectionModel().on({
                    scope: this,
                    rowselect: function (sm, index, record) {
                        this.observerNomeacaoPk(record.get('pk'));
                    },
                    rowdeselect: function (sm) {
                        this.observerNomeacaoPk(null);
                    }
                });
            }
            return this._nomeacaoGrid;
        },

        getNomeacaoAnexoGrid: function (cfg) {
            if (!this._anexo_nomeacaoGrid) {
                this._anexo_nomeacaoGrid = Ext._create('rh.nomeacao.anexo_nomeacao.Grid', {
                    region: 'center',
                    hideItemsToolbar: ['search', 'download'],
                    border: false,
                    height: 430,
                    gridAutoLoad: false
                });
                this._anexo_nomeacaoGrid.on({
                    scope: this,
                    createdItemGrid: function (instance) {
                        this.updateEmployeePanel();
                    },
                    updatedItemGrid: function (instance) {
                        this.updateEmployeePanel();
                    },
                    removedItemGrid: function (instance) {
                        this.updateEmployeePanel();
                    }
                });
            }
            return this._anexo_nomeacaoGrid;
        },








    }
);
