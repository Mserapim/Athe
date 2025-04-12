rh.employee.specialized.tab.fields.Provision = Ext.extend(
    rh.employee.specialized.tab.fields.Field,
    {
        constructor: function(cfg) {
            rh.employee.specialized.tab.fields.Provision.superclass.constructor.call(this, cfg);
        },

        observerEmployeePk: function(){
            rh.employee.specialized.tab.fields.Provision.superclass.observerEmployeePk.call(this, {});          
            if(this.myParams('employeePk')){
                this.getProvisionGrid().enable();
                this.getProvisionGrid().setParam('servidor', this.myParams('employeePk'));
                this.getProvisionGrid().setParam('is_member', this.myParams('is_member'));
                this.getProvisionGrid().setFilterProperty('servidor__pk', this.myParams('employeePk'), 100);
            }else{
                this.getProvisionGrid().setParam('servidor', undefined);
                this.getProvisionGrid().removeFilterProperty('servidor__pk', 100, false);
                this.getProvisionGrid().disable();
            }
        },

        fields: function(cfg){
            var items = [
                this.getProvisionGrid(cfg),
            ];
            return items;
        },

        getProvisionGrid: function(cfg) {
            if(!this._provisionGrid){
                this._provisionGrid = Ext._create('rh.movimentacao.possession.provision.Grid', {
                    gridAutoLoad: false,
                    ownerCfg: cfg,
                    height: 600,
                    scope: this,
                });
            }
            return this._provisionGrid;
        },
    }
);
